import asyncio
from typing import Callable, Dict, List, Optional, Set, Tuple

from todoesvan.data.model import Task
from todoesvan.services.task_service import TaskService

# Flet's page.run_task signature (roughly): run_task(coro_fn, *args)
Scheduler = Callable[..., None]
OnChange = Callable[[], None]
OnError = Callable[[str], None]


class TaskStore:
    """
    Owns:
      - two-list cache (pending/completed)
      - stale-while-revalidate refresh
      - optimistic create/delete/toggle + rollback
    Not UI-specific: it exposes state and triggers on_change when state updates.
    """

    def __init__(self, service: TaskService, schedule: Scheduler, on_change: OnChange, on_error: OnError):
        self.service = service
        self._schedule = schedule
        self._on_change = on_change
        self._on_error = on_error

        # ---- Cache ----
        self._cache: Dict[bool, List[Task]] = {False: [], True: []}  # False=pending, True=completed

        # Refresh state
        self._refreshing_tabs: Set[bool] = set()
        self._refresh_seq: int = 0
        self._refresh_token: Dict[bool, int] = {False: 0, True: 0}

        # Optimistic state
        self._pending_ids: Set[int] = set()
        self._pending_delete_ids: Set[int] = set()
        self._temp_id: int = -1

    # -------------------------
    # Public state getters
    # -------------------------
    @property
    def pending_ids(self) -> Set[int]:
        return self._pending_ids

    def tasks(self, completed: bool) -> List[Task]:
        return self._cache[completed]

    def is_refreshing(self, completed: bool) -> bool:
        return completed in self._refreshing_tabs

    # -------------------------
    # Public actions (UI calls these)
    # -------------------------
    def warm_cache_both(self) -> None:
        self._schedule(self._warm_cache_both)

    def refresh_tab(self, completed: bool) -> None:
        self._refresh_seq += 1
        token = self._refresh_seq
        self._refresh_token[completed] = token

        self._refreshing_tabs.add(completed)
        self._notify()

        self._schedule(self._refresh_tab_from_db, completed, token)

    def create_task(self, title: str) -> None:
        # Always add placeholder to Pending cache so it's instant.
        temp_id = self._temp_id
        self._temp_id -= 1

        placeholder = Task(id=temp_id, subject=title, completed=False)
        self._cache[False].insert(0, placeholder)
        self._pending_ids.add(temp_id)

        self._notify()
        self._schedule(self._persist_create_task, title, temp_id)

    def delete_task(self, task_id: int) -> None:
        found = self._find_anywhere(task_id)
        if not found:
            return

        key, idx = found
        removed = self._cache[key].pop(idx)

        self._pending_delete_ids.add(task_id)
        self._pending_ids.add(task_id)  # prevents refresh from resurrecting it

        self._notify()
        self._schedule(self._persist_delete_task, removed, key, idx)

    def toggle_completed(self, task_id: int, completed: bool) -> None:
        found = self._find_anywhere(task_id)
        if not found:
            return

        from_key, from_idx = found
        task = self._cache[from_key].pop(from_idx)
        old_completed = task.completed

        # Move to other list optimistically
        task.completed = completed
        to_key = completed
        self._cache[to_key].insert(0, task)

        self._pending_ids.add(task_id)
        self._notify()

        self._schedule(
            self._persist_toggle_completed,
            task_id,
            completed,
            old_completed,
            from_key,
            from_idx,
            to_key,
        )

    def update_subject(self, task_id: int, new_subject: str) -> None:
        found = self._find_anywhere(task_id)
        if not found:
            return

        cleaned = (new_subject or "").strip()
        if not cleaned:
            self._error("Task cannot be empty.")
            return

        key, idx = found
        task = self._cache[key][idx]
        old_subject = task.subject

        if cleaned == old_subject:
            return

        # Optimistic update
        task.subject = cleaned
        self._pending_ids.add(task_id)
        self._notify()

        self._schedule(self._persist_update_subject, task_id, cleaned, old_subject)


    # -------------------------
    # Internals
    # -------------------------
    def _notify(self) -> None:
        self._on_change()

    def _error(self, msg: str) -> None:
        self._on_error(msg)

    def _tasks_signature(self, tasks: List[Task]) -> List[Tuple[int, str, bool]]:
        return [(t.id, t.subject, t.completed) for t in tasks]

    def _find_anywhere(self, task_id: int) -> Optional[Tuple[bool, int]]:
        for key in (False, True):
            for i, t in enumerate(self._cache[key]):
                if t.id == task_id:
                    return key, i
        return None

    def _merge_with_local_overrides(self, completed_key: bool, server_tasks: List[Task]) -> List[Task]:
        # 1) never resurrect pending-deleted tasks
        tasks = [t for t in server_tasks if t.id not in self._pending_delete_ids]

        # 2) for pending toggles, prefer local state
        local_by_id: Dict[int, Task] = {}
        for t in self._cache[False] + self._cache[True]:
            if t.id > 0:
                local_by_id[t.id] = t

        pending_real_ids = [tid for tid in self._pending_ids if tid > 0 and tid not in self._pending_delete_ids]
        if pending_real_ids:
            pending_set = set(pending_real_ids)
            tasks = [t for t in tasks if t.id not in pending_set]

            for tid in pending_real_ids:
                lt = local_by_id.get(tid)
                if lt and lt.completed == completed_key:
                    tasks.insert(0, lt)

        # 3) keep optimistic create placeholders (negative IDs) at top of Pending list
        if completed_key is False:
            temp_tasks = [t for t in self._cache[False] if t.id < 0]
            if temp_tasks:
                tasks = temp_tasks + tasks

        return tasks

    # -------------------------
    # Refresh coroutines
    # -------------------------
    async def _warm_cache_both(self) -> None:
        self._refresh_seq += 1
        token_pending = self._refresh_seq
        self._refresh_seq += 1
        token_completed = self._refresh_seq

        self._refresh_token[False] = token_pending
        self._refresh_token[True] = token_completed

        self._refreshing_tabs.add(False)
        self._refreshing_tabs.add(True)
        self._notify()

        try:
            pending_task = asyncio.to_thread(self.service.get_tasks, False)
            completed_task = asyncio.to_thread(self.service.get_tasks, True)
            server_pending, server_completed = await asyncio.gather(pending_task, completed_task)

            if self._refresh_token[False] != token_pending or self._refresh_token[True] != token_completed:
                return

            new_pending = self._merge_with_local_overrides(False, server_pending)
            new_completed = self._merge_with_local_overrides(True, server_completed)

            if self._tasks_signature(new_pending) != self._tasks_signature(self._cache[False]):
                self._cache[False] = new_pending

            if self._tasks_signature(new_completed) != self._tasks_signature(self._cache[True]):
                self._cache[True] = new_completed

        finally:
            if self._refresh_token[False] == token_pending:
                self._refreshing_tabs.discard(False)
            if self._refresh_token[True] == token_completed:
                self._refreshing_tabs.discard(True)

            self._notify()

    async def _refresh_tab_from_db(self, completed_key: bool, token: int) -> None:
        try:
            server_tasks = await asyncio.to_thread(self.service.get_tasks, completed_key)

            if self._refresh_token[completed_key] != token:
                return

            merged = self._merge_with_local_overrides(completed_key, server_tasks)

            if self._tasks_signature(merged) != self._tasks_signature(self._cache[completed_key]):
                self._cache[completed_key] = merged
                self._notify()

        finally:
            if self._refresh_token[completed_key] == token:
                self._refreshing_tabs.discard(completed_key)
                self._notify()

    # -------------------------
    # Persist coroutines (optimistic)
    # -------------------------
    async def _persist_create_task(self, title: str, temp_id: int) -> None:
        try:
            created: Task = await asyncio.to_thread(self.service.add_task, title)
            idx = next((i for i, t in enumerate(self._cache[False]) if t.id == temp_id), -1)
            if idx != -1:
                self._cache[False][idx] = created

        except Exception as ex:
            idx = next((i for i, t in enumerate(self._cache[False]) if t.id == temp_id), -1)
            if idx != -1:
                self._cache[False].pop(idx)
            self._error(f"Create failed. Rolled back. ({ex})")

        finally:
            self._pending_ids.discard(temp_id)
            self._notify()

    async def _persist_delete_task(self, removed: Task, key: bool, original_index: int) -> None:
        try:
            await asyncio.to_thread(self.service.delete_task, removed.id)

        except Exception as ex:
            insert_at = min(max(original_index, 0), len(self._cache[key]))
            self._cache[key].insert(insert_at, removed)
            self._error(f"Delete failed. Rolled back. ({ex})")

        finally:
            self._pending_delete_ids.discard(removed.id)
            self._pending_ids.discard(removed.id)
            self._notify()

    async def _persist_toggle_completed(
        self,
        task_id: int,
        new_completed: bool,
        old_completed: bool,
        from_key: bool,
        from_idx: int,
        to_key: bool,
    ) -> None:
        try:
            await asyncio.to_thread(self.service.toggle_completed, task_id, new_completed)

        except Exception as ex:
            dst_idx = next((i for i, t in enumerate(self._cache[to_key]) if t.id == task_id), -1)
            task = self._cache[to_key].pop(dst_idx) if dst_idx != -1 else None

            if task:
                task.completed = old_completed
                insert_at = min(max(from_idx, 0), len(self._cache[from_key]))
                self._cache[from_key].insert(insert_at, task)

            self._error(f"Update failed. Rolled back. ({ex})")

        finally:
            self._pending_ids.discard(task_id)
            self._notify()

    async def _persist_update_subject(self, task_id: int, new_subject: str, old_subject: str) -> None:
        try:
            await asyncio.to_thread(self.service.update_subject, task_id, new_subject)

        except Exception as ex:
            # Rollback
            found = self._find_anywhere(task_id)
            if found:
                key, idx = found
                self._cache[key][idx].subject = old_subject

            self._error(f"Update failed. Rolled back. ({ex})")

        finally:
            self._pending_ids.discard(task_id)
            self._notify()

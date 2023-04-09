import os.path
import shutil
# from typing import Literal
from beaker import Application, GlobalStateValue
from beaker.consts import FALSE, TRUE
from beaker.lib.storage import BoxMapping
from pyteal import (
    Assert,
    Bytes,
    Expr,
    Global,
    If,
    Int,
    Itob,
    Pop,
    Seq,
    TealType,
    Txn,
    abi
)


class Task(abi.NamedTuple):
    owner: abi.Field[abi.Address]
    task_note: abi.Field[abi.String]
    is_completed: abi.Field[abi.Bool]
    time: abi.Field[abi.Uint64]


class State:
    task_id = GlobalStateValue(
        stack_type=TealType.uint64,
        default=Int(0),
        descr="Task tracker"
    )

    def __init__(self):
        self.tasks = BoxMapping(abi.Uint64, Task)
        self.min_fee = Int(2_000)


todo_app = Application("Todo", state=State())


@todo_app.external
def create_task(
        _txn: abi.PaymentTransaction,
        _task_note: abi.String
) -> Expr:
    return Seq(
        Assert(
            _txn.get().amount() >= todo_app.state.min_fee,
            _txn.get().receiver() == Global.current_application_address(),
            _txn.get().sender() == Txn.sender(),

            _task_note.get() != Bytes("")
        ),
        (owner := abi.Address()).set(Txn.sender()),
        (task_note := abi.String()).set(_task_note.get()),
        (is_completed := abi.Bool()).set(FALSE),
        (time := abi.Uint64()).set(Global.latest_timestamp()),

        (task := Task()).set(owner, task_note, is_completed, time),
        todo_app.state.tasks[Itob(todo_app.state.task_id)].set(task),

        todo_app.state.task_id.increment()
    )


@todo_app.external
def update_task(
        _task_id: abi.Uint64,
        _new_task_note: abi.String
) -> Expr:
    return Seq(
        (task := Task()).decode(todo_app.state.tasks[_task_id].get()),
        (owner := abi.Address()).set(task.owner),
        Assert(
            Txn.sender() == owner.get(),
            _new_task_note.get() != Bytes("")
        ),
        (new_task_note := abi.String()).set(_new_task_note),
        (is_completed := abi.Bool()).set(task.is_completed),
        (time := abi.Uint64()).set(task.time),

        task.set(owner, new_task_note, is_completed, time)
    )


@todo_app.external
def update_completed_status(_task_id: abi.Uint64):
    return Seq(
        (task := Task()).decode(todo_app.state.tasks[_task_id].get()),
        (owner := abi.Address()).set(task.owner),
        Assert(
            Txn.sender() == owner.get()
        ),
        (is_completed := abi.Bool()).set(task.is_completed),
        If(is_completed.get() == Int(0))
        .Then(is_completed.set(TRUE))
        .Else(is_completed.set(FALSE)),
        (task_note := abi.String()).set(task.task_note),
        (time := abi.Uint64()).set(task.time),

        task.set(owner, task_note, is_completed, time)
    )


@todo_app.external
def delete_task(_task_id: abi.Uint64) -> Expr:
    return Seq(
        (task := Task()).decode(todo_app.state.tasks[_task_id].get()),
        (owner := abi.Address()).set(task.owner),
        Assert(Txn.sender() == owner.get()),
        Pop(todo_app.state.tasks[_task_id].delete())
    )


@todo_app.external
def get_task(_task_id: abi.Uint64, *, output: Task) -> Expr:
    return output.decode(todo_app.state.tasks[_task_id].get())


if __name__ == "__main__":
    artifacts = "artifacts"
    if os.path.exists(artifacts):
        shutil.rmtree(artifacts)
    todo_app_spec = todo_app.build()
    todo_app_spec.export(artifacts)

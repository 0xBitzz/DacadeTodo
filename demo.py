from algosdk.abi import ABIType, Method
from algosdk.atomic_transaction_composer import ABIResult, TransactionWithSigner
from algosdk.transaction import PaymentTxn
from beaker import consts, sandbox
from beaker.client import ApplicationClient
from beaker.sandbox import SandboxAccount

from contract import todo as todo


todo_codec = ABIType.from_string(str(todo.Task().type_spec()))


class ApplicationCalls:
    @classmethod
    def make_payment_to_escrow(
            cls,
            acct_client: ApplicationClient,
            amount: int = 2_000
    ) -> TransactionWithSigner:
        return TransactionWithSigner(
            txn=PaymentTxn(
                sender=acct_client.sender,
                sp=acct_client.get_suggested_params(),
                receiver=acct_client.app_addr,
                amt=amount,
            ),
            signer=acct_client.signer
        )

    @classmethod
    def make_method_call(
            cls,
            acct_client: ApplicationClient,
            app_id: int,
            method_name: Method,
            box_name: bytes,
            **params
    ) -> ABIResult:
        result = acct_client.call(
            method=method_name,
            **params,
            boxes=[(app_id, box_name)]
        )
        return result


def print_boxes(app_client: ApplicationClient) -> None:
    boxes = app_client.get_box_names()
    print(f"{len(boxes)} boxes found!")
    for box_name in boxes:
        contents = app_client.get_box_contents(box_name)
        todo_task = todo_codec.decode(contents)
        print(f"{box_name} => {todo_task}")


def demo() -> None:
    creator_acct: SandboxAccount
    acct1: SandboxAccount
    acct2: SandboxAccount

    creator_acct, acct1, acct2 = sandbox.get_accounts()

    app_client = ApplicationClient(
        client=sandbox.get_algod_client(),
        app=todo.todo_app,
        signer=creator_acct.signer,
    )

    app_id, app_addr, tx_id = app_client.create()
    print(f"App created with ID: {app_id}, " +
          f"and address: {app_addr}, " +
          f"in transaction: {tx_id}")
    app_client.fund(consts.algo * 2)

    acct1_client = app_client.prepare(signer=acct1.signer)

    # Acct1 app calls
    # Create Task
    task_id = 0

    ApplicationCalls.make_method_call(
        acct_client=acct1_client,
        app_id=app_id,
        method_name=todo.create_task,
        box_name=task_id.to_bytes(8, "big"),
        _txn=ApplicationCalls.make_payment_to_escrow(acct_client=acct1_client),
        _task_note="Hello World!"
    )
    print_boxes(acct1_client)

    # Get task
    result = ApplicationCalls.make_method_call(
        acct_client=acct1_client,
        app_id=app_id,
        method_name=todo.get_task,
        box_name=task_id.to_bytes(8, "big"),
        _task_id=task_id
    )
    print(result.return_value)

    # Create Task
    task_id = 1

    ApplicationCalls.make_method_call(
        acct_client=acct1_client,
        app_id=app_id,
        method_name=todo.create_task,
        box_name=task_id.to_bytes(8, "big"),
        _txn=ApplicationCalls.make_payment_to_escrow(acct_client=acct1_client),
        _task_note="Hi World!"
    )
    print_boxes(acct1_client)

    # Get task
    result = ApplicationCalls.make_method_call(
        acct_client=acct1_client,
        app_id=app_id,
        method_name=todo.get_task,
        box_name=task_id.to_bytes(8, "big"),
        _task_id=task_id
    )
    print(result.return_value)

    # Delete Task
    task_id = 0

    ApplicationCalls.make_method_call(
        acct_client=acct1_client,
        app_id=app_id,
        method_name=todo.delete_task,
        box_name=task_id.to_bytes(8, "big"),
        _task_id=task_id
    )
    print_boxes(acct1_client)

    # Get task
    result = ApplicationCalls.make_method_call(
        acct_client=acct1_client,
        app_id=app_id,
        method_name=todo.get_task,
        box_name=task_id.to_bytes(8, "big"),
        _task_id=task_id
    )
    print(result.return_value)


demo()

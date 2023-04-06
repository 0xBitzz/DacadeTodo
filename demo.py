from contract import todo
from algosdk.abi import ABIType
from algosdk.atomic_transaction_composer import TransactionWithSigner
from algosdk.transaction import PaymentTxn
from beaker import consts, sandbox
from beaker.client import ApplicationClient


todo_codec = ABIType.from_string(str(todo.Task().type_spec()))


def print_boxes(app_client: ApplicationClient) -> None:
    boxes = app_client.get_box_names()
    print(f"{len(boxes)} boxes found!")
    for box_name in boxes:
        contents = app_client.get_box_contents(box_name)
        todo_task = todo_codec.decode(contents)
        print(f"{box_name} => {todo_task}")


def demo() -> None:
    accts = sandbox.get_accounts()

    creator_acct = accts.pop()
    acct1 = accts.pop()
    acct2 = accts.pop()

    app_client = ApplicationClient(
        client=sandbox.get_algod_client(),
        app=todo.todo_app,
        signer=creator_acct.signer
    )

    app_id, app_addr, tx_id = app_client.create()
    print(f"App created with ID: {app_id}, " +
          f"and address: {app_addr}, " +
          f"in transaction: {tx_id}")
    app_client.fund(consts.algo * 2)

    acct1_client = app_client.prepare(signer=acct1.signer)
    acct2_client = app_client.prepare(signer=acct2.signer)

    txn = TransactionWithSigner(
        txn=PaymentTxn(
            sender=acct1.address,
            sp=acct1_client.get_suggested_params(),
            receiver=app_addr,
            amt=2_000_000
        ),
        signer=acct1.signer
    )

    task_id = 0
    box_name = task_id.to_bytes(8, "big")
    acct1_client.call(
        todo.create_todo,
        _txn=txn,
        _task_note="Hi World!",
        boxes=[(app_id, box_name)]
    )
    print_boxes(acct1_client)

    task_id = 0
    box_name = task_id.to_bytes(8, "big")
    result = acct1_client.call(
        todo.get_task,
        _task_id=task_id,
        boxes=[(app_id, box_name)]
    )
    print(result.return_value)

    """
    task_id = 0
    box_name = task_id.to_bytes(8, "big")
    acct1_client.call(
        todo.update_todo,
        _task_id=0,
        _new_task_note="Hey World!",
        boxes=[(app_id, box_name)]
    )
    print_boxes(acct1_client)

    task_id = 0
    box_name = task_id.to_bytes(8, "big")
    result = acct1_client.call(
        todo.get_task,
        _task_id=task_id,
        boxes=[(app_id, box_name)]
    )
    print(result.return_value)
    """

    task_id = 0
    box_name = task_id.to_bytes(8, "big")
    acct1_client.call(
        todo.delete_todo,
        _task_id=0,
        boxes=[(app_id, box_name)]
    )
    print_boxes(acct1_client)

    task_id = 0
    box_name = task_id.to_bytes(8, "big")
    result = acct1_client.call(
        todo.get_task,
        _task_id=task_id,
        boxes=[(app_id, box_name)]
    )
    print(result.return_value)

    # txn = TransactionWithSigner(
    #     txn=PaymentTxn(
    #         sender=acct1.address,
    #         sp=acct1_client.get_suggested_params(),
    #         receiver=app_addr,
    #         amt=2_000_000
    #     ),
    #     signer=acct1.signer
    # )

    # task_id = 1
    # box_name = task_id.to_bytes(8, "big")
    # acct1_client.call(
    #     todo.create_todo,
    #     _txn=txn,
    #     _task_note="Hello World!",
    #     boxes=[(app_id, box_name)]
    # )
    # print_boxes(acct1_client)
    #
    # task_id = 1
    # box_name = task_id.to_bytes(8, "big")
    # result = acct1_client.call(
    #     todo.get_task,
    #     _task_id=task_id,
    #     boxes=[(app_id, box_name)]
    # )
    # print(result.return_value)
    #
    # # Update task
    # task_id = 1
    # box_name = task_id.to_bytes(8, "big")
    # acct1_client.call(
    #     todo.update_todo,
    #     _task_id=task_id,
    #     _new_task_note="Hey World",
    #     boxes=[(app_id, box_name)]
    # )
    # print_boxes(acct1_client)
    #
    # task_id = 1
    # box_name = task_id.to_bytes(8, "big")
    # result = acct1_client.call(
    #     todo.get_task,
    #     _task_id=task_id,
    #     boxes=[(app_id, box_name)]
    # )
    # print(result.return_value)


demo()

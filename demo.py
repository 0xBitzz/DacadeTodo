from contract import todo
from algosdk.abi import ABIType
from algosdk.atomic_transaction_composer import TransactionSigner, TransactionWithSigner
from algosdk.transaction import PaymentTxn, SuggestedParams
from beaker import consts, sandbox
from beaker.client import ApplicationClient

todo_codec = ABIType.from_string(str(todo.Task().type_spec()))


class Transaction:
    def __init__(
            self,
            acct_addr: str,
            acct_signer: TransactionSigner,
            rcv_addr: str,
            sp: SuggestedParams,
            amount: int = 2_000
    ):
        self.acct_addr = acct_addr
        self.acct_signer = acct_signer
        self.rcv_addr = rcv_addr
        self.sp = sp
        self.amount = amount

    def spawn_new_txn(self):
        txn = TransactionWithSigner(
            txn=PaymentTxn(
                sender=self.acct_addr,
                sp=self.sp,
                receiver=self.rcv_addr,
                amt=self.amount
            ),
            signer=self.acct_signer
        )
        return txn


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

    task_id = 0
    box_name = task_id.to_bytes(8, "big")
    acct1_client.call(
        todo.create_todo,
        _txn=Transaction(
            acct_addr=acct1.address,
            acct_signer=acct1.signer,
            rcv_addr=app_addr,
            sp=acct1_client.get_suggested_params(),
        ).spawn_new_txn(),
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
    Update method
    
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

    # task_id = 0
    # box_name = task_id.to_bytes(8, "big")
    # acct1_client.call(
    #     todo.delete_todo,
    #     _task_id=0,
    #     boxes=[(app_id, box_name)]
    # )
    # print_boxes(acct1_client)
    #
    # task_id = 0
    # box_name = task_id.to_bytes(8, "big")
    # result = acct1_client.call(
    #     todo.get_task,
    #     _task_id=task_id,
    #     boxes=[(app_id, box_name)]
    # )
    # print(result.return_value)

    task_id = 1
    box_name = task_id.to_bytes(8, "big")
    acct1_client.call(
        todo.create_todo,
        _txn=Transaction(
            acct_addr=acct1.address,
            acct_signer=acct1.signer,
            rcv_addr=app_addr,
            sp=acct1_client.get_suggested_params(),
        ).spawn_new_txn(),
        _task_note="Hello World!",
        boxes=[(app_id, box_name)]
    )
    print_boxes(acct1_client)

    task_id = 1
    box_name = task_id.to_bytes(8, "big")
    result = acct1_client.call(
        todo.get_task,
        _task_id=task_id,
        boxes=[(app_id, box_name)]
    )
    print(result.return_value)


demo()

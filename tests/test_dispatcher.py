from actions.dispatcher import BasicActionDispatcher


dispatcher = BasicActionDispatcher()

result = dispatcher.dispatch(
    "computer_action",
    "Open Calculator"
)

print(result)
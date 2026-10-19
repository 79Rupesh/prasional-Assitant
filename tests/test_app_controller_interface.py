from core.interfaces.app_controller import AppControllerProvider


class TestAppController(AppControllerProvider):

    def open(self, app_name: str) -> str:
        return f"Opening {app_name}"

    def close(self, app_name: str) -> str:
        return f"Closing {app_name}"


controller = TestAppController()

print(controller.open("Safari"))
print(controller.close("Safari"))
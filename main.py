import asyncio

from viam.module.module import Module
from viam.components.camera import Camera
from viam.resource.registry import Registry, ResourceCreatorRegistration
from oak_camera import OakCamera

async def main():
    Registry.register_resource_creator(Camera.SUBTYPE, OakCamera.MODEL, ResourceCreatorRegistration(OakCamera.new))

    module = Module.from_args()
    module.add_model_from_registry(Camera.SUBTYPE, OakCamera.MODEL)
    await module.start()

if __name__ == "__main__":
    asyncio.run(main())
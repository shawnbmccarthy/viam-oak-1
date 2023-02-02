import viam.media.video
import depthai
from depthai_sdk import OakCamera
import PIL
from threading import Thread, Lock
from typing import Dict, Any, Optional, Tuple, Union
from PIL import Image
from viam.components.camera import Camera, DistortionParameters, IntrinsicParameters


class OakCameraThread(Thread):
    def __init__(self) -> None:
        """

        """
        self.running = False
        self.current_image = None
        self.lock = Lock()
        # which variables need to be object scoped?
        self.pipeline = None
        self.cam_rgb = None
        self.xout_rgb = None
        self._setup_pipeline()
        self.running = True
        super().__init__()

    def _setup_pipeline(self):
        self.pipeline = depthai.Pipeline()
        self.cam_rgb = self.pipeline.create(depthai.node.ColorCamera)
        self.cam_rgb.setPreviewSize(300, 300)
        self.cam_rgb.setBoardSocket(depthai.CameraBoardSocket.RGB)
        self.cam_rgb.setResolution(depthai.ColorCameraProperties.SensorResolution.THE_1080_P)
        self.cam_rgb.setInterleaved(False)
        self.cam_rgb.setColorOrder(depthai.ColorCameraProperties.ColorOrder.RGB)
        self.xout_rgb = self.pipeline.create(depthai.node.XLinkOut)
        self.xout_rgb.setStreamName('rgb')

    def get_image(self):
        return self.current_image

    def run(self) -> None:
        print(f'starting ...')
        with depthai.Device(self.pipeline) as device:
            q_rgb = device.getOutputQueue('rgb', maxSize=1, blocking=False)
            while self.running:
                in_rgb = q_rgb.get()

                if in_rgb is not None:
                    print(f'in_rgb type: {type(in_rgb)}')
                    self.lock.acquire()
                    try:
                        print(f'w: {in_rgb.getWidth()}, h: {in_rgb.getHeight()}')
                        self.current_image = Image.frombytes(
                            'RGBA',
                            (in_rgb.getWidth(), in_rgb.getHeight()),
                            in_rgb.getCvFrame()
                        )
                    finally:
                        self.lock.release()
                else:
                    print(f'else in_rgb: {in_rgb}')

    def stop(self) -> None:
        self.running = False


class OakCamera(Camera):
    def __init__(self, name: str) -> None:
        """

        :param name:
        """
        self.props = Camera.Properties(
            supports_pcd=False,
            distortion_parameters=DistortionParameters(),
            intrinsic_parameters=IntrinsicParameters()
        )
        self.oct = OakCameraThread()
        self.oct.start()
        super().__init__(name)

    async def get_image(
            self,
            mime_type: str = '',
            *,
            timeout: Optional[float] = None,
            **kwargs
    ) -> Union[PIL.Image.Image, viam.media.video.RawImage]:
        """

        :param mime_type:
        :param timeout:
        :param kwargs:
        :return:
        """
        raise NotImplemented('todo')

    async def get_point_cloud(
            self,
            *,
            timeout: Optional[float] = None,
            **kwargs
    ) -> Tuple[bytes, str]:
        """

        :param timeout:
        :param kwargs:
        :return:
        """
        raise NotImplemented('point cloud not supported')

    async def get_properties(
            self,
            *,
            timeout: Optional[float] = None,
            **kwargs
    ) -> viam.components.camera.camera.Camera.Properties:
        """

        :param timeout:
        :param kwargs:
        :return:
        """
        return self.props

    async def do_command(
            self,
            command: Dict[str, Any],
            *,
            timeout: Optional[float] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """

        :param command:
        :param timeout:
        :param kwargs:
        :return:
        """
        raise NotImplemented('do command not implemented')

import viam.media.video
import depthai
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
        self.xout_rgb = self.pipeline.create(depthai.node.XLinkOut)
        self.xout_rgb.setStreamName('rgb')
        self.cam_rgb.setPreviewSize(300, 300)
        self.cam_rgb.setInterleaved(False)
        self.cam_rgb.setColorOrder(depthai.ColorCameraProperties.ColorOrder.RGB)
        self.cam_rgb.preview.link(self.xout_rgb.input)

    def get_image(self):
        return self.current_image

    def run(self) -> None:
        with depthai.Device(self.pipeline) as device:
            q_rgb = device.getOutputQueue('rgb', maxSize=1, blocking=False)
            while self.running:
                in_rgb = q_rgb.tryGet()

                if in_rgb is not None:
                    data = in_rgb.getRaw().data.data
                    self.lock.acquire()
                    try:
                        self.current_image = Image.frombytes('RGBA', (128, 128), data, 'raw')
                    finally:
                        self.lock.release()

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
        return self.oct.get_image()

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

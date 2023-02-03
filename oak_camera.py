import blobconverter
import viam.media.video
import depthai
import cv2
import PIL
import numpy as np
from threading import Thread, Lock
from typing import Dict, Any, Optional, Tuple, Union
from PIL import Image
from viam.components.camera import Camera, DistortionParameters, IntrinsicParameters


def frame_norm(frame, bbox):
    norm_values = np.full(len(bbox), frame.shape[0])
    norm_values[::2] = frame.shape[1]
    return (np.clip(np.array(bbox), 0, 1) * norm_values).astype(int)


class OakCameraThread(Thread):
    def __init__(self) -> None:
        """

        """
        self.running = False
        self.current_image = None
        self.lock = Lock()
        self.running = True
        super().__init__()

    def get_image(self):
        """

        :return:
        """
        return self.current_image

    def run(self) -> None:
        """

        :return:
        """
        print(f'starting ...')
        pipeline = depthai.Pipeline()
        cam_rgb = pipeline.createColorCamera()
        cam_rgb.setPreviewSize(300, 300)
        cam_rgb.setInterleaved(False)

        detection_nn = pipeline.createMobileNetDetectionNetwork()
        detection_nn.setBlobPath(blobconverter.from_zoo(name='mobilenet-ssd', shaves=6))
        detection_nn.setConfidenceThreshold(0.5)
        cam_rgb.preview.link(detection_nn.input)

        xout_rgb = pipeline.createXLinkOut()
        xout_rgb.setStreamName('rgb')
        cam_rgb.preview.link(xout_rgb.input)

        xout_nn = pipeline.createXLinkOut()
        xout_nn.setStreamName('nn')
        detection_nn.out.link(xout_nn.input)

        with depthai.Device(pipeline) as device:
            q_rgb = device.getOutputQueue('rgb')
            q_nn = device.getOutputQueue('nn')
            frame = None
            detections = []

            while self.running:
                in_rgb = q_rgb.tryGet()
                in_nn = q_nn.tryGet()

                if in_rgb is not None:
                    frame = in_rgb.getCvFrame()

                if in_nn is not None:
                    detections = in_nn.detections

                if frame is not None:
                    for detection in detections:
                        bbox = frame_norm(frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
                        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)
                        self.lock.acquire()
                        try:
                            f_tmp = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            self.current_image = Image.fromarray(f_tmp)
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

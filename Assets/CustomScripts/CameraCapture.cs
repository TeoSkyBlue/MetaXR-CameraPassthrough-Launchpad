using UnityEngine;
using Meta.XR;

public class CameraCapture : MonoBehaviour
{
    public PassthroughCameraAccess cameraAccess;
    private int framecount = 0;

    void Start()
    {
        Debug.Log("CameraCapture: Start()");

        if (cameraAccess == null)
        {
            Debug.LogError(
                "CameraCapture: cameraAccess reference missing"
            );
        }
        else
        {
            Debug.Log("CameraCapture: cameraAccess reference found");
        }
    }
    void Update()
    {
        framecount++;
        if (framecount < 30)
            return;
        framecount = 30;

        if (cameraAccess == null)
            return;
        
        Texture image = cameraAccess.GetTexture();
        
        if (image != null )
        {
            Debug.Log("Camera image received: " + image.width + "x" + image.height);
            var timestamp = cameraAccess.Timestamp;
            var cameraPose = cameraAccess.GetCameraPose();
            var intrinsics = cameraAccess.Intrinsics;
            byte[] jpeg = CameraImageEncoder.EncodeJpeg(image);

            if (jpeg != null)
            {
                //TODO: Pass data along to the network sender.
            }

        }
    }
}

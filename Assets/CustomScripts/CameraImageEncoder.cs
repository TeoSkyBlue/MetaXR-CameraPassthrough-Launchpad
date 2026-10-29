using UnityEngine;

//TODO: Encoder at some point should be working in the background in a child thread for obvious performance reasons.

public static class CameraImageEncoder
{
    public static byte[] EncodeJpeg(Texture source, int quality = 80) //should probably increase this at some point
    {
        if (source == null)
                return null;

        RenderTexture renderTex = RenderTexture.GetTemporary(source.width, source.height, 0, RenderTextureFormat.ARGB32);

        RenderTexture prevTex = RenderTexture.active;
        Texture2D cpuTexture = null;

        try
        {
            Graphics.Blit(source, renderTex);
            RenderTexture.active = renderTex;

            cpuTexture = new Texture2D(source.width, source.height, TextureFormat.RGB24, false);
            cpuTexture.ReadPixels(new Rect(0, 0, renderTex.width, renderTex.height), 0, 0);
            cpuTexture.Apply(false, false);

            return cpuTexture.EncodeToJPG(quality);

        
        }
        finally
        {
            RenderTexture.active = prevTex;
            RenderTexture.ReleaseTemporary(renderTex);

            if (cpuTexture != null)
                Object.Destroy(cpuTexture);
        }
    }
}

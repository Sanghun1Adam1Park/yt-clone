/* eslint-disable @typescript-eslint/no-explicit-any */
import { httpsCallable } from 'firebase/functions';
import { functions } from './firebase';

// Wraps cloud function into JS callable. 
const generateUploadUrlFunction = httpsCallable(functions, "generateUploadUrl");
const getVideosFunction = httpsCallable(functions, 'getVideos');

export interface Video {
  id?: string,
  uid?: string,
  filename?: string,
  status?: 'processing' | 'processed',
  title?: string,
  description?: string  
}

/**
 * Uploads a video file from the client by:
 * 1. Requesting a signed upload URL from a Cloud Function
 * 2. Uploading the video directly to Cloud Storage using that URL
 *
 * @param file The video file to upload
 * @returns The result of the upload fetch request
 */
export async function uploadVideo(file: File) {
    // Wait for cloud function to response upload url
    const response: any = await generateUploadUrlFunction({
        // Only need file extension as part of data outside of actual video
        fileExtension: file.name.split('.').pop()
    });

    // make http request using upload url
    const uploadResult = await fetch(response?.data?.url, {
        method: "PUT", // http method
        body: file, // payload
        headers: {
            "Content-Type": file.type,
        },
    });

    console.log(uploadResult)
    return uploadResult
}

/**
 * Get videos from firestore.
 * @returns videos
 */
export async function getVideos() {
  const response = await getVideosFunction();
  return response.data as Video[];
}
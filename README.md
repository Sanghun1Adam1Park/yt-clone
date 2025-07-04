# vid-sharing-platform-clone
This project replicates a popular video-sharing platform to better understand microservices, cloud-based environments, and system design. The primary focus is on architectural decisions rather than feature-complete implementation or metric-driven optimization.

## Tech Stack Overview 

### video processing
- Cloud Services: Google Cloud (Bucket, Pub/Sub, Cloud Run)
- Backend: FastAPI (Python)
    - why? allows concurrent req handling. 
- Proccessing Logic: FFmpeg 

### Cloud API services & Authentication 
- Upload Url Provide: Firebase Function, Firestore 
- Backend: Node.js (TypeScript)
    - why? because of better SDK support. 

### UI
- Next.js (TypeScript)

### Containerization
- Docker

## Version 1.0 Flow Charts 
Rather than implementing full UX features like subscriptions, comments, or video metadata editing (e.g., thumbnails and titles), this version focuses on the core system components such as video uploading, processing, and querying. The goal is to demonstrate and validate high-level system design rather than build a complete production-ready application.

### Sign in 
![Sign-in Flowchart](imgs/Sign-in-flowchart.png) 

1. User sign-in via Google OAuth.
2. Firebase Authentication verifies the user.
	- If this is the user’s first login, their basic info (email, name) is saved to Firestore.
3. Once authenticated, the Next.js frontend updates its state to reflect the signed-in status.

### Upload 
![Upload Flowchart](imgs/Upload-flowchart.png)

0. User must be authenticated. 
1. User presses 'upload' button.
2. Firebase function provides user with uplaod URL.
3. UI uploads video to gcloud buckets for raw-videos.
    1. Buckets sends notifaciton to pub/sub.
    2. Pub/sub calls vidoe process service via api-endpoint.
    3. Cloud run function checks if videos are already in process or not.
    4. If not in process, function starts processing the vidoe.
        1. Downloads raw video from raw-video bucket.
        2. Process, then uploads to processed-video bucket.
    5. After vidoes are done being processed, 
4. Response 

### Watching a Video  
![Watch Video Flowchart](imgs/Watch-video-flowchart.png)

1. User opens the UI app.
2. UI app feteches videos via fir

### Notable Limitations 
There are several limitations beyond the intentionally excluded UX features (e.g., comments, subscriptions, etc.).

#### Long-living HTTP request 
For each pub/sub request, it must be awknowledge within 600 seconds. However, the cloud run could take up to 3600 seconds to process the video. In such case, although the video will not be re-uploaded/duplicated using status on firestore, the request itself will be re-tried for next 7 days leaving it un-resovled. 

#### Long-Processing time
If the video is so large so that it takes more than 60 minutes (3600 seconds) to process, then cloud run will shut down the video-processing container. This results in failed processing and no retry mechanism at the compute level unless explicitly handled.

## Fixes
In this section, we discuss about improvement of system/adding missing components from previous versions.

### Solution to Long-living Pub/Sub messages, Handling long video-process, and Video-process error hanlding.

#### Long living Pub/Sub messages
The issue with version 1.0 system with Pub/Sub messages was that, if the process was to take longer than 600 seconds which is the maximum wait time for Pub/Sub to recieve `awk` back. In such system, this can happen quite often becasue processing video can take long time (if video is large enough). So, the solution to this problem was to reverse relation between Pub/Sub and Cloud run. Using google scheduler, now the cloud run point checks wether there are pull message in the queue in Pub/sub and can extend the `awk` deadline if needed. 

![Process Worker Flowchart](imgs/Process-worker-flowchart.png)

#### Process error handling 
To ensure that future request for corrupted processing can be handled properly, we just have to make sure that-firestore deletes the docuemt for future re-upload. 

#### Long video process 
As mentitoned previously, if the process is longer than an hour, cloud run terminates the process and deems it as failure. This can be critical for such service, because processing long videos, can take quite some time. 

The solution to this was to bring back push pub/sub message, but with slight twist.
In this design, cloud run endpoint serves purpose of caller instead of worker and service. The job of cloud run endpoint is to call cloud run job which can handle long process, since it's just calling, it response immediately which then solves both problems: long living http request and hanlding long video porcess. 
The flow looks like this: 
1. bucket creates notifcaiton 
2. pub/sub pushes message to caller service
3. caller service calls goolge job  

> There is no picture to describe in this section :\

### Other & New issues 
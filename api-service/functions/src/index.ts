/**
 * Import function triggers from their respective submodules:
 *
 * import {onCall} from "firebase-functions/v2/https";
 * import {onDocumentWritten} from "firebase-functions/v2/firestore";
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

import * as functions from "firebase-functions/v1";
import {initializeApp} from "firebase-admin/app";
import {Firestore} from "firebase-admin/firestore";
import * as logger from "firebase-functions/logger";
import {Storage} from "@google-cloud/storage";
import {onCall} from "firebase-functions/v2/https";

initializeApp();
const firestore = new Firestore(); // FB store object.

export interface Video {
  id?: string,
  uid?: string,
  filename?: string,
  status?: "processing" | "processed";
  title?: string,
  description?: string
}

// Cloud Function that runs when a new user signs
// up via Firebase Authentication.
export const createUser = functions.region("europe-west3").auth.user()
  .onCreate((user) => {
    const userInfo = {
      uid: user.uid,
      email: user.email,
      photoUrl: user.photoURL,
    };

    firestore.collection("users").doc(user.uid).set(userInfo);
    logger.info(`User Created: ${JSON.stringify(userInfo)}`);
    return;
  });

const storage = new Storage();

// Callable HTTPS (clound) function to generate
// a signed upload URL when invoked by an authenticated client.
export const generateUploadUrl = onCall(
  {
    region: "europe-west3",
    maxInstances: 1,
  },
  async (request) => {
    // Check if uesr that invoked request is authenticated.
    if (!request.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "The function can only be called while authenticated."
      );
    }

    const auth = request.auth;
    const data = request.data;
    const bucket = storage.bucket("yt-clone-raw-06280527");
    const filename = `${auth.uid}-${Date.now()}.${data.fileExtension}`;

    // Get the url from (upload) bucket
    const [url] = await bucket.file(filename).getSignedUrl({
      version: "v4",
      action: "write",
      expires: Date.now() + 15 * 60 * 1000, // 15 minutes
    });

    return {url, filename};
  }
);

export const getVideos = onCall(
  {
    region: "europe-west3",
    maxInstances: 1,
  },
  async () => {
    const snapshot =
      await firestore.collection("videos").limit(20).get();
    return snapshot.docs.map((doc) => doc.data());
  }
);

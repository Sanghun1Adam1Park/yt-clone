import { initializeApp } from "firebase/app";
import { 
    getAuth, 
    onAuthStateChanged, 
    signInWithPopup, 
    User,
    GoogleAuthProvider 
} from "firebase/auth";


// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

/**
 * Signs the user in with a google popup.
 * @returns A promise that resolves with the user's crednetials.
 */
export function signInWithGoogle() {
    return signInWithPopup(auth, new GoogleAuthProvider());
}

/**
 * Signs the user out.
 * @returns A promise that resolves when the user is signed out.
 */
export function signOut() {
    return auth.signOut();
}

/**
 * Subscribes to Firebase Auth state changes and triggers the given callback on each change.
 * @param callback - A function called with the current user or null on each auth change.
 * @returns A function to unsubscribe from further auth state updates.
 */
export function onAuthStateChangedHelper(callback: (user: User | null) => void) {
    // Listens for authentication state changes from Firebase Auth as side effect.
    // Triggers the provided callback with the user or null whenever auth state changes.
    // Returns an unsubscribe function to stop listening when called.
    return onAuthStateChanged(auth, callback); 
}
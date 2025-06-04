"use client";

import Image from "next/image";
import Link from "next/link";
import SignIn from "./sign-in";

import { useEffect, useState } from "react";
import { onAuthStateChangedHelper } from "../../firebase/firebase";
import { User } from "firebase/auth";

export default function HeaderBar() {
  // `user` stores the currently authenticated Firebase user (or null)
  // setUser - funciton to update the user state.
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
      // Use side effect of onAuthStateCHangedHelepr(callback)
      const unsubscribe = onAuthStateChangedHelper(
        (user) => {setUser(user);} // null menas firebase did not detect any auth user
      );
    
      return () => { 
        unsubscribe(); // stop using the side effect.
      }
  }, []); // Runs once - to set up listner and listner handles effect of state changes. 

  return (
    <header className='
        flex
        justify-between
        items-center
        p-4
    '> 
      <Link href="/">
        <Image width={150} height={120}
          src="/yt-clone-logo.svg" alt="YouTube Logo"/>
      </Link>
      <SignIn user={user} />
    </header>
  );
}

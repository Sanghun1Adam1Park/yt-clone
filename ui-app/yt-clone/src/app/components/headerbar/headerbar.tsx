"use client";

import Image from "next/image";
import Link from "next/link";
import SignIn from "./sign-in";

import { useEffect, useState } from "react";
import { onAuthStateChangedHelper } from "../../firebase/firebase";
import { User } from "firebase/auth";

// TODO: Understand fr. 
export default function HeaderBar() {
  // State - data managed by component that can change over time
  // setUser - funciton to update the user state.
  const [user, setUser] = useState<User | null>(null);

  useEffect(
    () => {
      const unsubscribe = onAuthStateChangedHelper(
        (user) => {setUser(user);}
      );
    
      return () => unsubscribe();
    }, []
  );

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

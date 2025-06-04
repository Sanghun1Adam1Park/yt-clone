import { User } from "firebase/auth";
import { signOut, signInWithGoogle } from '../../firebase/firebase';

interface AppUser {
    /* defining shape of the object */
    user: User | null; // is a User or null. 
}

export default function SignIn({user} : AppUser) {
    return (
        <div className="
            inline-block
            border border-gray-400
            text-[#065fd4] text-[14px]
            font-medium font-roboto 
            px-5
            rounded-full
            cursor-pointer
            hover:bg-[#bee0fd] 
            hover:border-transparent
        ">
            {user ? ( // if user
                <button onClick={signOut}> 
                    Sign Out
                </button>
            ) : ( // if null
                <button onClick={signInWithGoogle}>
                    Sign In
                </button>
            )}
        </div>
    )
}
import { User } from "firebase/auth";
import SignIn from "../user_button/sign-in";
import Upload from "../user_button/upload";

export interface AppUser {
    /* defining shape of the object */
    user: User | null; // is a User or null. 
}

export default function UserButton({ user }: AppUser) {
    return (
        <header className='
        flex
        justify-between
        items-center
        p-4'> 
            <SignIn user={user} />
            <Upload user={user} />
        </header>
    )
}
import React from "react";
import { uploadVideo } from "../../firebase/functions";
import { AppUser } from "../headerbar/user-button";

export default function Upload({user}: AppUser) {
    const handleUpload = async (file: File) => {
        try {
            const response = await uploadVideo(file);
            alert(`File uploaded succssfully. Server responded with ${JSON.stringify(response)}`);
        } catch (error) {
            alert(`Failed to upload file: ${error}`);
        }
    }
    
    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.item(0);
        if (file) {
            handleUpload(file);
        }
    };

    return (
        <>  
            <label htmlFor="upload" className="
                flex justify-center items-center
                w-[25px] h-[25px] rounded-[50%]
                text-black border-none cursor-pointer
                text-[10px] p-[0.4em]">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.2} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" d="M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 002.25-2.25v-9a2.25 2.25 0 00-2.25-2.25h-9A2.25 2.25 0 002.25 7.5v9a2.25 2.25 0 002.25 2.25z" />
                </svg>
            </label>
            <input id="upload" className="hidden"
                type="file"
                accept="video/*"
                onChange={handleFileChange}
                disabled={!user}></input>
        </>
    )
}
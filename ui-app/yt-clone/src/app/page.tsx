import Link from "next/link";
import Image from 'next/image';
import { getVideos } from "./firebase/functions";

export default async function Home() {
  const videos = await getVideos(); 
  
  return (
    <main>
      {
        videos.map((video) => 
          <Link 
            key={video.id}
            href={`/watch?v=${video.filename}`}>
            <Image src={'/thumbnail.png'} alt='video' width={120} height={80}
              className="m-[10px]"/>
          </Link>
        ) 
      }
    </main>
  );
}

// Rerender every 30 seconds, limit cacheing 
export const revalidate = 30; 
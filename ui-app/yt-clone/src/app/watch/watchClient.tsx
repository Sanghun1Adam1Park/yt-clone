'use client';

import { useSearchParams } from 'next/navigation'

export default function WatchClient() {
  const endpoint = "https://storage.googleapis.com/yt-clone-processed-06280527/"
  const videoName = useSearchParams().get('v'); 

  console.log(endpoint + videoName)

  return (
    <div>
      <h1>Watch Page</h1>
      { <video controls src={endpoint + videoName}/> }
    </div>
  );
}

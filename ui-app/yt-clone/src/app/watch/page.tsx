import { Suspense } from 'react'
import WatchClient from './watchClient'

export default function Watch() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <WatchClient />
    </Suspense>
  )
}
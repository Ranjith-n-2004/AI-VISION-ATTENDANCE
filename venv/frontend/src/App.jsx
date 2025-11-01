import CameraFeed from './components/CameraFeed'
import AddFaceForm from './components/AddFaceForm'
import Navbar from './components/Navbar'

function App() {
  // Realtime events removed per request

  return (
    <div className="min-h-screen bg-gray-900 text-white pb-6">
      <Navbar cameraActive={true} />
      
      <main className="container mx-auto px-4 py-8">
        <CameraFeed />
        <div className="mt-8">
          <AddFaceForm />
        </div>
      </main>
    </div>
  )
}

export default App

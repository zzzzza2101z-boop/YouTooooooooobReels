import React, {useState} from 'react'

export default function App(){
  const [youtube, setYoutube] = useState('')
  const [password, setPassword] = useState('')
  const [status, setStatus] = useState('')

  const start = async ()=>{
    setStatus('جاري المعالجة...')
    try{
      const res = await fetch('/api/process',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({youtube, password})
      })
      const j = await res.json()
      if(res.ok){
        setStatus('تم! حمل الريل: ' + j.reel)
      } else {
        setStatus('خطأ: ' + (j.error||''))
      }
    }catch(e){
      setStatus('حصل خطأ: ' + e.message)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white p-6 font-sans">
      <div className="max-w-3xl mx-auto bg-black/40 p-6 rounded-2xl shadow-2xl">
        <h1 className="text-3xl mb-4">مولد ريلز خاص - نسخة شخصية</h1>
        <input className="w-full p-3 rounded mb-3 text-black" placeholder="رابط YouTube" value={youtube} onChange={e=>setYoutube(e.target.value)} />
        <input className="w-full p-3 rounded mb-3 text-black" placeholder="كلمة المرور الخاصة" value={password} onChange={e=>setPassword(e.target.value)} />
        <button onClick={start} className="bg-indigo-600 px-4 py-2 rounded">ابدأ</button>
        <p className="mt-4">{status}</p>
      </div>
    </div>
  )
}

import ChatInterface from "@/components/chat-interface";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-neutral-950 text-neutral-100 p-4 md:p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex mb-8">
        <p className="fixed left-0 top-0 flex w-full justify-center border-b border-neutral-800 bg-neutral-950/50 pb-6 pt-8 backdrop-blur-2xl lg:static lg:w-auto lg:rounded-xl lg:border lg:bg-neutral-900/50 lg:p-4">
          Multimodal Chat &nbsp;
          <code className="font-mono font-bold">v2.0</code>
        </p>
        <div className="fixed bottom-0 left-0 flex h-48 w-full items-end justify-center bg-gradient-to-t from-neutral-950 via-neutral-950/50 to-transparent lg:static lg:h-auto lg:w-auto lg:bg-none">
          <span className="pointer-events-none flex place-items-center gap-2 p-8 lg:pointer-events-auto lg:p-0">
            Powered by Ollama
          </span>
        </div>
      </div>

      <div className="w-full max-w-4xl h-[80vh] relative flex flex-col rounded-3xl border border-neutral-800 bg-neutral-900/50 backdrop-blur-sm shadow-2xl overflow-hidden">
        <ChatInterface />
      </div>
    </main>
  );
}

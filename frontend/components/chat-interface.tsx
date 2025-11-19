"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Image as ImageIcon, Loader2, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";

interface Message {
    role: "user" | "assistant";
    content: string;
    image?: string;
}

export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setSelectedImage(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setImagePreview(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const clearImage = () => {
        setSelectedImage(null);
        setImagePreview(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if ((!input.trim() && !selectedImage) || isLoading) return;

        const userMessage: Message = {
            role: "user",
            content: input,
            image: imagePreview || undefined,
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        // Create FormData
        const formData = new FormData();
        formData.append("prompt", userMessage.content || "Describe this image"); // Default prompt if only image
        if (selectedImage) {
            formData.append("image", selectedImage);
        } else {
            // Handle text-only if needed, but backend expects image currently.
            // For now, let's assume image is required as per backend spec, 
            // or we can update backend to make it optional.
            // The current backend REQUIRES an image.
            if (!selectedImage) {
                setMessages((prev) => [...prev, { role: "assistant", content: "Please select an image first. This is a multimodal chat." }]);
                setIsLoading(false);
                return;
            }
        }

        try {
            const response = await fetch("http://localhost:8000/analyze", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) throw new Error("Failed to fetch response");
            if (!response.body) throw new Error("No response body");

            setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantMessage = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                assistantMessage += chunk;

                setMessages((prev) => {
                    const newMessages = [...prev];
                    newMessages[newMessages.length - 1].content = assistantMessage;
                    return newMessages;
                });
            }

            // Clear image after successful send
            clearImage();

        } catch (error) {
            console.error(error);
            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: "Sorry, something went wrong. Please try again." },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full w-full bg-neutral-900/30">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-neutral-700 scrollbar-track-transparent">
                {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-neutral-500 space-y-4">
                        <ImageIcon className="w-16 h-16 opacity-20" />
                        <p>Upload an image and ask a question to get started.</p>
                    </div>
                )}

                <AnimatePresence>
                    {messages.map((msg, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`flex w-full ${msg.role === "user" ? "justify-end" : "justify-start"
                                }`}
                        >
                            <div
                                className={`max-w-[80%] rounded-2xl p-4 ${msg.role === "user"
                                        ? "bg-blue-600 text-white rounded-br-none"
                                        : "bg-neutral-800 text-neutral-200 rounded-bl-none"
                                    }`}
                            >
                                {msg.image && (
                                    <div className="mb-3 rounded-lg overflow-hidden border border-white/10">
                                        <img src={msg.image} alt="User upload" className="max-w-full h-auto max-h-64 object-cover" />
                                    </div>
                                )}
                                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-neutral-800 rounded-2xl rounded-bl-none p-4 flex items-center space-x-2">
                            <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                            <span className="text-neutral-400 text-sm">Thinking...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-neutral-900/80 border-t border-neutral-800 backdrop-blur-md">
                {imagePreview && (
                    <div className="mb-4 relative inline-block">
                        <div className="relative rounded-xl overflow-hidden border border-neutral-700 group">
                            <img src={imagePreview} alt="Preview" className="h-20 w-auto object-cover" />
                            <button
                                onClick={clearImage}
                                className="absolute top-1 right-1 bg-black/50 hover:bg-red-500/80 text-white rounded-full p-1 transition-colors opacity-0 group-hover:opacity-100"
                            >
                                <X className="w-3 h-3" />
                            </button>
                        </div>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="flex items-end gap-3">
                    <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        ref={fileInputRef}
                        onChange={handleImageSelect}
                    />

                    <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        className={`p-3 rounded-xl transition-colors ${selectedImage
                                ? "bg-blue-500/20 text-blue-400 border border-blue-500/50"
                                : "bg-neutral-800 text-neutral-400 hover:bg-neutral-700 hover:text-neutral-200"
                            }`}
                    >
                        <ImageIcon className="w-5 h-5" />
                    </button>

                    <div className="flex-1 relative">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={selectedImage ? "Ask about the image..." : "Select an image first..."}
                            className="w-full bg-neutral-800 text-white rounded-xl px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder:text-neutral-600"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading || (!input.trim() && !selectedImage)}
                        className="p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg shadow-blue-900/20"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </form>
            </div>
        </div>
    );
}

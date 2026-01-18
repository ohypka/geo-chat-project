"use client";
import { createContext, useState, ReactNode } from "react";
import { Msg } from "../components/Chat/types";

type ChatContextType = {
    messages: Msg[];
    setMessages: (msgs: Msg[]) => void;
    mapData?: any;
    setMapData: (data: any) => void;
    layerType?: string;
    setLayerType: (type: string) => void;
};

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatContextProvider = ({ children }: { children: ReactNode }) => {
    const [messages, setMessages] = useState<Msg[]>([]);
    const [mapData, setMapData] = useState<any>();
    const [layerType, setLayerType] = useState<string>();

    return (
        <ChatContext.Provider value={{ messages, setMessages, mapData, setMapData,layerType, setLayerType }}>
            {children}
        </ChatContext.Provider>
    );
};

export default ChatContext;

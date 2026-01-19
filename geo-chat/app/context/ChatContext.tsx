"use client";
import { createContext, useState, ReactNode } from "react";

type ChatContextType = {
    mapData?: any;
    setMapData: (data: any) => void;
    layerType?: string;
    setLayerType: (type: string) => void;
    mapOpen: boolean;
    setMapOpen: (v: boolean) => void;
};

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatContextProvider = ({ children }: { children: ReactNode }) => {
    const [mapData, setMapData] = useState<any>();
    const [layerType, setLayerType] = useState<string>();
    const [mapOpen, setMapOpen] = useState(false);

    return (
        <ChatContext.Provider value={{ mapData, setMapData,layerType, setLayerType, mapOpen, setMapOpen }}>
            {children}
        </ChatContext.Provider>
    );
};

export default ChatContext;

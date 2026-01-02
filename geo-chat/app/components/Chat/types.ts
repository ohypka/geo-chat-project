export type Role = "user" | "assistant";
export type Thread = { id: string; title: string };

export type TextMsg = { id: string; role: Role; type: "text"; content: string };
export type MapMsg = { id: string; role: Role; type: "map"; title?: string; subtitle?: string };

export type Msg = TextMsg | MapMsg;

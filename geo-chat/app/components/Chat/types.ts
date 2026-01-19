export type Role = "user" | "assistant";
export type Thread = { id: string; title: string };

type BaseMsg = {
  id: string;
  role: Role;
  content?: string;
  mapData?: any;
  layerType?: string;
  title?: string;
  subtitle?: string;
};

export type TextMsg = BaseMsg & {
  type: "text";
};

export type MapMsg = BaseMsg & {
  type: "map";
};

export type Msg = TextMsg | MapMsg;


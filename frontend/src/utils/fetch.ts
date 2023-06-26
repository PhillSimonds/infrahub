import { QSP } from "../config/qsp";

export const fetchUrl = async (url: string, payload?: any) => {
  const newPayload = {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...payload?.headers,
    },
    method: payload?.method ?? "GET",
    ...(payload?.method === "POST"
      ? {
          body: payload?.body ?? "",
        }
      : {}),
  };

  const rawResponse = await fetch(url, newPayload);

  return rawResponse?.json();
};

const read = async (reader: any): Promise<string> => {
  const result = await reader.read();

  const currentValue = new TextDecoder().decode(result.value);

  if (result.done) {
    return currentValue;
  }

  const nextResult = await read(reader);

  return `${currentValue} ${nextResult}`;
};

export const fetchStream = async (url: string, payload?: any) => {
  const response = await fetch(url, payload);

  if (!response.ok) {
    return "No file content";
  }

  const stream = response.body; // ReadableStream object
  const reader = stream?.getReader();

  const result = await read(reader); // Returns a promise that resolves with a chunk of data

  return result;
};

const QSP_TO_INCLUDE = [QSP.BRANCH];

// Construct link with path that contains all QSP
export const constructPath = (path: string) => {
  const { href } = window.location;

  const url = new URL(href);

  const { searchParams } = url;

  // Get QSP as [ [ key, value ], ... ]
  const params = Array.from(searchParams)
    .filter(
      ([k]) => QSP_TO_INCLUDE.includes(k) // Remove some QSP if not needed to be forwarded
    )
    .filter(
      ([k]) => !path.includes(k) // If a QSP is already in the path, then we don't override it
    );

  // Construct the new params as "?key=value&..."
  const newParams = params.length
    ? params.reduce(
        (acc, [k, v], index) => `${acc}${k}=${v}${index === params.length - 1 ? "" : "&"}`,
        "?"
      )
    : "";

  return `${path}${newParams}`;
};

// Update a QSP in the URL (add, update or remove it)
export const updateQsp = (qsp: string, newValue: string, setSearchParams: Function) => {
  const { href } = window.location;

  const url = new URL(href);

  const { searchParams } = url;

  // Get QSP as [ [ key, value ], ... ]
  const params = [...Array.from(searchParams), [qsp, newValue]];

  // Construct the new params as { [name]: value }
  const newParams = params.reduce(
    (acc, [k, v]) => ({
      ...acc,
      [k]: v,
    }),
    {}
  );

  console.log("newParams: ", newParams);
  return setSearchParams(newParams);
};

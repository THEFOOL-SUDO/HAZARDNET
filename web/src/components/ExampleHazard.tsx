// web/src/components/ExampleHazard.tsx
import React, { useState } from "react";

type Props = { keyword: string; region?: string };

export default function ExampleHazard({ keyword, region }: Props) {
  const [hover, setHover] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const query = encodeURIComponent(`${keyword} ${region || ""} news`.trim());
  const ytUrl = `https://www.youtube.com/results?search_query=${query}`;

  return (
    <div className="inline-block relative">
      <span
        tabIndex={0}
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
        onFocus={() => setHover(true)}
        onBlur={() => setHover(false)}
        className="underline cursor-pointer"
      >
        {keyword}
      </span>

      {hover && (
        <div className="absolute z-20 mt-2 p-2 bg-white border rounded shadow">
          <div>{`Example: ${keyword}`}</div>
          <button
            className="mt-2 px-3 py-1 bg-blue-600 text-white rounded"
            onClick={() => setShowModal(true)}
          >
            Show related news
          </button>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40">
          <div role="dialog" aria-modal="true" className="bg-white p-4 rounded shadow" style={{ minWidth: 320 }}>
            <p>
              Open YouTube news results for <b>{keyword}</b> {region ? `in ${region}` : ""}?
            </p>
            <div className="mt-4 flex gap-2">
              <button
                className="px-3 py-1 bg-green-600 text-white rounded"
                onClick={() => {
                  window.open(ytUrl, "_blank", "noreferrer");
                  setShowModal(false);
                }}
              >
                Accept
              </button>
              <button className="px-3 py-1 bg-gray-300 rounded" onClick={() => setShowModal(false)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

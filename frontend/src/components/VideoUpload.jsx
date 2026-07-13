import { useState, useRef, useCallback } from "react";
import styles from "./VideoUpload.module.css";

const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export default function VideoUpload({ onResult }) {
  const [file, setFile]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  /* ── File handling ── */
  const handleFile = useCallback((f) => {
    if (!f || !f.type.startsWith("video/")) return;
    setFile(f);
  }, []);

  const removeFile = (e) => {
    e.stopPropagation();
    setFile(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  /* ── Drag events ── */
  const onDragOver  = (e) => { e.preventDefault(); setDragging(true);  };
  const onDragLeave = (e) => { e.preventDefault(); setDragging(false); };
  const onDrop      = (e) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    handleFile(dropped);
  };

  /* ── Upload ── */
  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res  = await fetch(`${API_URL}/upload`, { method: "POST", body: formData });
      const data = await res.json();
      onResult(data);
    } catch (err) {
      console.error(err);
      onResult({ status: "error", message: "Upload failed. Make sure the backend is running." });
    }
    setLoading(false);
  };

  /* ── Zone click (only when no file) ── */
  const onZoneClick = () => {
    if (!file && !loading && inputRef.current) inputRef.current.click();
  };

  /* ── Classes ── */
  const zoneClass = [
    styles.dropzone,
    dragging  ? styles.dragging : "",
    file      ? styles.hasFile  : "",
  ].filter(Boolean).join(" ");

  return (
    <div className={styles.wrapper}>
      {/* Drop Zone */}
      <div
        className={zoneClass}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={onZoneClick}
        role="button"
        tabIndex={file || loading ? -1 : 0}
        onKeyDown={(e) => e.key === "Enter" && onZoneClick()}
        aria-label="Upload video file"
      >
        {/* Hidden file input */}
        <input
          ref={inputRef}
          type="file"
          accept="video/*"
          className={`${styles.fileInput} ${styles.hidden}`}
          onChange={(e) => handleFile(e.target.files[0])}
          aria-hidden="true"
          tabIndex={-1}
        />

        {/* ── Loading State ── */}
        {loading && (
          <div className={styles.loadingState}>
            <div className={styles.spinner} />
            <p className={styles.loadingTitle}>Analyzing your speech…</p>
            <div className={styles.loadingSteps}>
              <span className={styles.loadingStep}>
                <span className={styles.loadingDot} />
                <span className={styles.loadingDot} />
                <span className={styles.loadingDot} />
                Transcribing audio with Whisper
              </span>
              <span className={styles.loadingStep}>
                <span className={styles.loadingDot} />
                <span className={styles.loadingDot} />
                <span className={styles.loadingDot} />
                Detecting eye contact with MediaPipe
              </span>
            </div>
          </div>
        )}

        {/* ── File Selected ── */}
        {!loading && file && (
          <div className={styles.fileInfo}>
            <div className={styles.fileChip}>
              <span className={styles.fileChipIcon}><VideoIcon /></span>
              <span className={styles.fileChipName}>{file.name}</span>
              <button
                className={styles.fileChipRemove}
                onClick={removeFile}
                aria-label="Remove file"
              >
                <CloseIcon />
              </button>
            </div>
            <button
              className={styles.analyzeBtn}
              onClick={handleUpload}
              disabled={loading}
            >
              <AnalyzeIcon />
              Analyze My Speech
            </button>
          </div>
        )}

        {/* ── Idle ── */}
        {!loading && !file && (
          <>
            <div className={styles.idleIcon}><UploadIcon /></div>
            <p className={styles.dropzoneTitle}>Drop your video here</p>
            <p className={styles.dropzoneHint}>or</p>
            <span className={styles.browseBtn}>
              <BrowseIcon /> Browse Files
            </span>
            <p className={styles.supportedTypes}>MP4, MOV, AVI, WEBM</p>
          </>
        )}
      </div>
    </div>
  );
}

/* ── Inline SVG Icons ── */
function UploadIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="16 16 12 12 8 16" />
      <line x1="12" y1="12" x2="12" y2="21" />
      <path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3" />
    </svg>
  );
}

function VideoIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="23 7 16 12 23 17 23 7" />
      <rect x="1" y="5" width="15" height="14" rx="2" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

function AnalyzeIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
      <line x1="11" y1="8" x2="11" y2="14" />
      <line x1="8" y1="11" x2="14" y2="11" />
    </svg>
  );
}

function BrowseIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  );
}

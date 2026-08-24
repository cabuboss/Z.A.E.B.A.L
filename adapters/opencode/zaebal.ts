// Z.A.E.B.A.L. — OpenCode adapter.
// Zaebal? Audit. Errors. Break. Analize. Leave no assumption.
//
// On every user message, runs the shared python core against the message
// text and injects the escalation protocol (if any) as a synthetic part.
// Fail-open: any error (no python3, timeout, core crash) is a silent no-op.

import { spawnSync } from "child_process"
import { createHash } from "crypto"
import { mkdir, rename, writeFile } from "fs/promises"
import { homedir } from "os"
import { join } from "path"
import type { Plugin } from "@opencode-ai/plugin"

const CORE = join(homedir(), ".zaebal", "core", "zaebal.py")
const TRANSCRIPT_DIR = join(homedir(), ".zaebal", "transcripts", "opencode")

export async function snapshotSession(
  client: any,
  sessionID: string,
  directory: string,
  currentMessage: any,
  currentText: string,
  transcriptDir = TRANSCRIPT_DIR,
): Promise<string | null> {
  try {
    const response = await client.session.messages({
      sessionID,
      directory,
    })
    if (!Array.isArray(response.data)) return null
    const messages = response.data
    const rows = messages.map((entry: any) => ({
      timestamp: entry?.info?.time?.created ?? "",
      role: entry?.info?.role ?? "unknown",
      content: (entry?.parts ?? [])
        .filter((part: any) => part?.type === "text" && typeof part.text === "string")
        .map((part: any) => part.text)
        .join("\n"),
      message_id: entry?.info?.id ?? "",
    }))
    const currentMessageID = currentMessage?.id
    if (!currentMessageID || !rows.some((row: any) => row.message_id === currentMessageID)) {
      rows.push({
        timestamp: currentMessage?.time?.created ?? Date.now(),
        role: "user",
        content: currentText,
        message_id: currentMessage?.id ?? "",
      })
    }

    await mkdir(transcriptDir, { recursive: true })
    const name = createHash("sha256").update(sessionID).digest("hex") + ".jsonl"
    const target = join(transcriptDir, name)
    const temporary = `${target}.${process.pid}.${Date.now()}.tmp`
    const body = rows
      .filter((row: any) => row.content)
      .map((row: any) => JSON.stringify(row))
      .join("\n") + "\n"
    await writeFile(temporary, body, { encoding: "utf8", mode: 0o600 })
    await rename(temporary, target)
    return target
  } catch {
    return null
  }
}

export const ZaebalPlugin: Plugin = async ({ client, directory }) => {
  return {
    "chat.message": async (input, output) => {
      try {
        const text = (output.parts as any[])
          .filter((p) => p && p.type === "text" && typeof p.text === "string")
          .map((p) => p.text)
          .join("\n")
        if (!text.trim()) return

        const probePayload = JSON.stringify({ prompt: text })
        const probe = spawnSync(
          "python3",
          [CORE, "--host", "opencode", "--classify-only"],
          { input: probePayload, encoding: "utf8", timeout: 10000 },
        )
        const kind = (probe.stdout ?? "").trim()
        const transcriptPath = kind === "directed" || kind === "ambiguous"
          ? await snapshotSession(
              client,
              input.sessionID ?? "unknown",
              directory ?? "",
              output.message,
              text,
            )
          : null

        const payload = JSON.stringify({
          session_id: input.sessionID ?? "unknown",
          prompt: text,
          cwd: directory ?? "",
          transcript_path: transcriptPath,
          transcript_complete: transcriptPath !== null,
        })
        const result = spawnSync("python3", [CORE, "--host", "opencode"], {
          input: payload,
          encoding: "utf8",
          timeout: 120000,
        })
        const injected = (result.stdout ?? "").trim()
        if (result.status === 0 && injected) {
          ;(output.parts as any[]).unshift({
            type: "text",
            text: injected,
            synthetic: true,
          })
        }
      } catch {
        // fail-open: never break the session because of zaebal
      }
    },
  }
}

export default ZaebalPlugin

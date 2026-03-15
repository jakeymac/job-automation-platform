import cronstrue from "cronstrue"

export function readableSchedule(schedule: string): string {
  try {
    const parts = schedule.trim().split(" ")
    // cron must have at least 5 parts
    if (parts.length < 5) {
      return "Invalid schedule"
    }
    return cronstrue.toString(schedule)
  } catch {
    return "Invalid schedule"
  }
}
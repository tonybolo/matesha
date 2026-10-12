import skillsData from '../../../content/skills.yaml'

export type SkillInfo = { title: string; topic: string; step: number }

export const skills = skillsData as Record<string, SkillInfo>

export function skillInfo(id: string): SkillInfo | undefined {
  return skills[id]
}

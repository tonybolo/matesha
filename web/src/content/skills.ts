export type SkillInfo = { title: string; topic: string; step: number }

// Навыки лежат по одному файлу на раздел: content/skills/algebra.yaml, geometry.yaml, stats.yaml
const files = import.meta.glob('../../../content/skills/*.yaml', {
  import: 'default',
  eager: true,
}) as Record<string, Record<string, SkillInfo>>

export const skills: Record<string, SkillInfo> = Object.assign({}, ...Object.values(files))

export function skillInfo(id: string): SkillInfo | undefined {
  return skills[id]
}

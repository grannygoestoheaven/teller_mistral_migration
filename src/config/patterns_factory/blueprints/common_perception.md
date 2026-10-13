{
  "blueprints": [
    {
      "name": "The Historical Assumption",
      "structure": "Since [era/event], {{ subject }} has been synonymous with [common trait]—a reputation cemented by [iconic example]. Yet this obscures its [unexpected role/mechanism]...",
      "example": {
        "rendered": "Since the Renaissance, {{ subject }} have been symbols of [common trait], immortalized in [iconic example]. But their true mastery lies in precision: [technical detail]."
      }
    },
    {
      "name": "The Cultural Shorthand",
      "structure": "Pop culture casts {{ subject }} as [stereotype]—think [movie/scene/meme]. Beneath that, though, it’s a [scientific/technical marvel]...",
      "example": {
        "rendered": "From [cultural reference] to [modern use], {{ subject }} are shorthand for [stereotype]. Yet their real genius is in [scientific field]: [surprising fact]."
      }
    },
    {
      "name": "The Contradictory First Impression",
      "structure": "At first glance, {{ subject }} seems [obvious trait]. But that’s a side effect of [hidden process]—the real story is...",
      "example": {
        "rendered": "At first glance, {{ subject }} simply [common action]. But that’s a [type of trick]—they actually [true mechanism], a quirk that reveals [insight]."
      }
    },
    {
      "name": "The Overlooked Origin",
      "structure": "We associate {{ subject }} with [modern use], but it was originally designed for [obscure purpose]. That legacy explains why...",
      "example": {
        "rendered": "Today, {{ subject }} [modern use], but their first mass-produced use was in [historical context]—where [technical trait] helped [original purpose]."
      }
    },
    {
      "name": "The Misattributed Power",
      "structure": "{{ subject }} is credited with [common effect], but the heavy lifting is done by [unsung mechanism]. For example...",
      "example": {
        "rendered": "{{ subject }} are praised for [common effect], but the illusion relies on [mechanism]: [explanation]."
      }
    },
    {
      "name": "The Unseen Labor",
      "structure": "{{ subject }} appears effortless—[common experience]—yet that simplicity masks [complex system]...",
      "example": {
        "rendered": "A {{ subject }}’s [action] seems [adjective], but the [material/component] is a [technical description], [explanation]."
      }
    }
  ],
  "design_notes": [
    "Replace placeholders (e.g., [era/event], [common trait]) with subject-specific details.",
    "For automated rendering, pass a dictionary with keys like `subject`, `common_trait`, `technical_detail`, etc.",
    "Example usage:",
    "{% set subject = 'mirrors' %}",
    "{% set common_trait = 'vanity' %}",
    "{% set technical_detail = 'a flat mirror’s reflection is the only optical system to produce a perfect, distortion-free virtual image' %}",
    "{{ blueprints[0].example.rendered | replace('[common trait]', common_trait) | replace('[technical detail]', technical_detail) }}"
  ]
}

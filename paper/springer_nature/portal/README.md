# Submission portal copy

The text in portal_copy.txt is extracted from the latest HawkFranklin report.
Standalone title.txt, abstract.txt and keywords.txt contain only those fields.
The source hash and abstract word count are recorded in source_manifest.json.
No manuscript prose or scientific results were changed.

The target is Nature Machine Intelligence and the proposed type is Reusability
Report. These are preparation files, not a completed portal submission.

## Before Submission

- The current abstract exceeds the journal's published 150-word Article limit.
  Reusability Reports are described as Articles; confirm whether the editor or
  portal grants a different limit for this format before using the full abstract.
  Do not shorten only the portal abstract without aligning the manuscript.
- Confirm the title, author names, coauthor email, ORCID details and full
  affiliation as required by the portal.
- Confirm approval by both authors and that the manuscript is not under
  consideration elsewhere. The cover-letter draft does not invent these
  declarations. Add the confirmed declarations before submission.
- Confirm funding, ethics, related submissions or preprints and any prior
  editorial correspondence. These were not inferred from another paper.
- Ensure reviewers can access the private frozen-fold dataset where needed.
- Check article-type requirements, including display-item limits. The report has
  five main figures and three tables, plus Extended Data. No manuscript formatting
  or compliance changes have been made in this task.

The example cover letter contains unrelated signed author-agreement material.
None of its signatures, author data or embedded images was copied.

## Rebuild

Run prepare_portal.py with the Codex document runtime Python. It regenerates
portal text and cover_letter.docx from the manuscript and cover_letter_portal.txt.
If you edit the Word letter, transfer those edits to the text draft before rebuild.

Official guidance consulted on 7 October 2026:

- https://www.nature.com/natmachintell/content
- https://www.nature.com/documents/natmachintell-brief-submission-guide.pdf
- https://support.nature.com/en/support/solutions/articles/6000245673-cover-letter-for-your-manuscript

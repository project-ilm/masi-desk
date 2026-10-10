# Venue, docket, and provenance desk

Standalone description for review. Canon as of 6 October 2026, plus the operational layer needed to implement it. Not an implementation.

What was agreed in the design conversation is canon. Review notes are incorporated only where they add an operational contract. They do not narrow the desk. Nothing in this document is hard-wired. Roles, rules, transition matrices, gates, forms, and outlets are configuration. Each has a default, so a launch without choices behaves like the academic workflow people already know.

A person, a group, or an institution can plan, launch, and execute a journal, a book, or a conference, and can manage their own submissions, their IRB, and their intellectual property. The default experience is that familiar workflow. Every departure is a configurable option, offered beside the work, not announced as the system.

The desk is the product. Author, reviewer, editor, chair, reader, and IRB member each get a face that feels like a submission system. It is built from public forge events and the indexes those events write. It is not a thinner record of some other product.

## Invariants

These hold under every configuration.

- A DOI is never unpublished. A later version, a retraction notice, or a withdrawal of endorsement is appended.
- A venue decision never destroys an author-held DOI. Rejection, withdrawal, and non-inclusion leave that DOI in place.
- A venue submission is a distinct matter linked to the author-held work. Venue state never rewrites the work’s own provenance.
- Inclusion does not make the venue the owner of the author’s DOI.
- Events are append-only. Current state is derived. Editing a current-state file does not erase the event that produced the previous state.
- Indexes are deterministic projections. They can always be regenerated from the matter and event records. An index is not an independent source of truth.
- Two valid transitions cannot silently overwrite one another. A transition names the parent event it expected. If that is no longer the tip, the transition fails and must be rebased.
- A public disclosure cannot subsequently become secret. A trade secret never enters the forge.
- G3, when enabled, blocks a public mint while a linked patent is unfiled, unless defensive publication is set.
- G4, when enabled, blocks acceptance and later inclusion without a recorded review. A desk reject is not an acceptance. A placeholder review can record a decision made elsewhere.
- A later assessment never modifies an earlier assessment.
- A publisher DOI is never fabricated. It is recorded when supplied.
- Policy is versioned. Each consequential transition records the policy version under which it occurred.
- The complete history of a matter is reconstructable from the repository and its external provenance records, including when the dashboard, the API, or Pages is unavailable.
- Git history remains authoritative when the presentation layer is down.
- Every state transition produces exactly one event, committed atomically with the state and index changes it causes. `event_id` is immutable and unique within the repository. `parent_event` is the causal chain and is never inferred from wall-clock order.
- A matter may have several independently evolving dimensions. The fold produces the whole current state, not one scalar. Default dimensions are venue, review, publication, program, IRB, and IP. A container may add one.
- A forge commit is not a public disclosure merely because it exists. Disclosure occurs when the object is accessible to the public, or is deposited into a public registry or outlet. A private venue repository during review is not, by that commit, a disclosure.
- The policy records the encryption envelope and the key-delivery mechanism. Encrypting a review to a reviewer’s key, and encrypting it under a per-review key that is then wrapped to that key, are both allowed. The record says which.

## Existing pieces

Four pieces already exist. The desk uses them. It does not replace them.

Misty publishes a citable object. One canonical `misty.json` goes in. Out comes a package: the artifact, its SHA-256, a Zenodo body, DataCite, `codemeta.json`, `CITATION.cff`, and a manifest. With a Zenodo token, publish mints a real Zenodo DOI. The first publish mints a concept DOI. Later publishes of the same work are versions under that concept, not new concepts. A DOI is a dated public disclosure. Guard runs before a mint. Browser deposit keeps the token in the tab. `author_verified` is a package default and, on this desk, a container setting.

Tok is existence: evidence that the identified bytes were presented to the chain at or before the recorded time. It is not, by itself, authorship, ownership, originality, or legal priority. It is not a DOI mint. The chain is SHA-256, then OpenTimestamps, then AyeSHA, then an append-only registry, then a Tok record. The unit can be a byte, a word, a message, a fragment, or a file. No Zenodo token is required. The raw `.ots` proof is not stored. Only its AyeSHA encoding is. The registrar is a browser page. The submitter puts the record in `registry/<id>/inbox/`, and `ingest.sh` folds it in. Two registries ship: `general`, and `pie` for endorsements of the Proclamation of Individual Equity. A Tok record is a sub-DOI. A collection of them is what Misty can publish as one Zenodo DOI. A public Tok registry is itself a disclosure. AyeSHA as shipped is a placeholder codec. The interface is stable. The codec is not.

Candor authorizes an irreversible step. One command, a short digest, a reason, an in-toto statement stamped with OpenTimestamps, then mint or push. It sits in `attest/`.

MASI is the ledger of a matter. As shipped it tracks ethics, preregistration, paper, journal, conference, chapter, and patent. The gates remain available. A container may disable or loosen a gate. The default is the gates as shipped.

- G1. Human-subjects work needs a linked IRB matter approved before collection. An approval cannot be applied backwards. Expiry warns, and under the default blocks further collection until renewed.
- G2. A preregistration stamp must predate collection, or it is a post-hoc plan.
- G3. A linked patent matter still in drafting or disclosed blocks a mint, unless `defensive_publication` is set.
- G4. Accepted, and every later included or published state, needs a recorded review. A placeholder review can record an outside decision.
- G5. A linked preregistration that never reached registered warns. Human-subjects work with no preregistration warns.

`mintable` means no error-level gate. Warnings do not block unless the container says they do.

The provenance order is seal, clear, attest, mint. Seal is Tok. Clear is `misty guard`. Attest is Candor. Mint is Misty.

The desk records legal and ethical facts supplied by the rights holder, the investigator, or counsel. It does not determine legal validity, ownership, registrability, or enforceability. Recording a filing number does not file. Recording an IRB approval does not grant one.

## Records

Every object the desk uses has a canonical machine-readable schema. Human-facing views are projections. Indexes are derived. Schemas are versioned and extensible. A container may add fields. It may not remove a field the default workflow writes. Unknown fields are preserved, not dropped.

Default records:

- `container.json` — kind (journal, book, conference), title, ISSN or ISBN if held, license, policy version, switches, reserved DOI.
- `policy.json` — the versioned switch set. Matters point at the version in force at each transition.
- `person.json` — canonical person. Forge login is the authentication mechanism, not the identity. A person may link a GitHub account, an ORCID, an affiliation, and a display name. Name changes append. The old name remains.
- `matter.json` — one venue submission, one chapter, one IRB protocol, or one IP right. Links to the author-held work and to the policy version.
- `work.json` — the author-held object. Its DOI, its hash, its versions. Venue matters link here. They do not own it.
- `submission.json` — the issue number, the attachment or the mount pointer, the submitted-on date, the co-author list.
- `assessment.json` — dated, signed, recommendation, optional grade. Append-only.
- `review.json` — round, scores, confidence, comments to authors, comments to committee, recommendation. Body stored clear, as a hash, or as ciphertext, per policy.
- `decision.json` — the standing at a time. Points at the assessment. Does not replace it.
- `decision-letter.json` — kind, sent-at, hash, Tok stamp. Body only if the holder keeps it.
- `revision.json` — parent version, new hash, note.
- `event.json` — append-only transition record, defined below.
- `session.json`, `presentation.json`, `track.json`, `issue.json` (journal issue), `chapter.json`.
- `irb.json` — the IRB matter, defined below.
- `ip-matter.json` — patent, trademark, design, copyright, or trade secret.
- `notification.json` — kind, recipients, sent-at, hash. Delivery status if an adapter reports it.
- `docket-entry.json` — venue, issue URL, state, decision, DOI.
- `mount.json` — pointer for bytes that do not live in git.
- `index/papers.json`, `index/sessions.json` — regenerable projections.

An event has: `event_id`, `event_type`, `actor`, `timestamp`, `matter_id`, `previous_state`, `new_state`, `reason`, `evidence`, `commit`, `parent_event`, and a signature or Candor attestation where the act is irreversible. Current state is the fold of events. A force-push that drops events is a policy violation, refused on the protected branch.

## Default transition matrix

The matrix is configuration. This is the default. A container may add a transition, name who may initiate it, and name the evidence and the gate. It may not, under the default policy, make acceptance terminal.

Journal, default. Prepared to submitted needs a venue and a date, author initiates, file frozen and Tok-stamped. Submitted to desk-check, editor. Desk-check to under-review, or to rejected with no review required. Under-review to reviews-received. Reviews-received to major-revision, minor-revision, accepted, or rejected. Accepted needs `accepted_on` and a review record. Major or minor revision to resubmitted, author. Resubmitted to under-review. Accepted to copyedit, proof, published. Published needs `published_on`. Any non-terminal state to withdrawn, by the author, or by the editor if policy allows. Any state, including published, may receive a later assessment. A later reject appends. It does not edit the accept.

Conference, default. Prepared to abstract-submitted. Abstract-submitted to abstract-accepted or rejected. Abstract-accepted to full-submitted. Then the same review loop as a journal, plus rebuttal as a transition out of reviews-received and back. Accepted to camera-ready. Camera-ready to presented, which needs `presented_on` and talk or poster. Presented and proceedings-published do not imply each other. There is no default cap on revision or rebuttal rounds. A cap is a setting, off by default.

Book, default. A chapter moves proposed, invited, drafting, submitted, editor-review, revising, final, in-production, published. The book publishes when the editor says it is ready, including with a chapter dropped. Dropped is an event, not a deletion.

Who may initiate a transition is the permission matrix, not a constant in code.

## Roles, identity, permissions

Forge login authenticates. The person record is the identity. GitHub, GitLab, ORCID, and an institutional identifier are links on that person. A person without a forge account can be named on a matter. They cannot act until a login is linked. Reviewer identity in a blind setting is the person record held with the salt, not the public issue.

Default roles: author, co-author, corresponding author, reviewer, handling editor, area chair, chair, board member, IRB member, IRB chair, reader. A container may add a role. A chair may grant a role on one track without granting it on the repository. That grant is a file, scoped to the track, expiring if the container sets an expiry. CODEOWNERS is the default reflection of the board, not the only way to delegate.

Default permissions. Author: submit, revise, withdraw before a venue rule forbids it, retract an author-minted submission. Co-author: the same, once accepted onto the matter, if that setting is on. Reviewer: read the assigned item, file a review, decline. Editor and chair: assign, remind, decide, accept, reject, publish, retract a venue version, change policy. Reader: see what policy marks public. System workflows: stamp, index, mint when the transition says so. IRB chair: approve, refuse, amend, renew. No role is hard-wired. This table is the default file.

Policy changes after submissions exist are themselves events. They apply to later transitions. They do not rewrite the policy version recorded on earlier ones. Who may change policy is the chair and the editor, by default.

## Co-authors

Configurable. Default, matching current practice: the submitting author lists co-authors, order is significant, one corresponding author is marked, and a co-author does not have to click accept before the submission is filed. The alternative, off by default, requires each co-author to accept before the matter can move to under-review.

Removing an author, adding one, or reordering is an event. The old list remains. Whether the change requires a new version of the work is a setting. The default is that an authorship change after submission is a new version of the venue matter, linked to the same work.

## Conflicts

Configurable. Default is a declared conflict note on the assignment, visible to the chair, not to the public index. Automatic institutional matching, and a block on assignment, are settings, off by default. Who may override a conflict is the chair. An override is an event with a reason.

## Review confidentiality

Three modes, container setting. Closed is the default. Open writes the report in the clear. Encrypted writes ciphertext in the public repository.

Blind is off by default. When on, the public issue carries a hash of the identifier mixed with a salt. The salt is held by the unblinder, in a private repository or another secret store the container names. Matching is joining the public hash to the salt. Unblinding is releasing the match.

Key lifecycle is configuration. Default: the chair generates a per-review key, the workflow encrypts to the reviewer’s published key if they have one, otherwise the key is mailed once. The editor can decrypt under the default, so a lost reviewer key does not lose the review. Rotation, reviewer-only decryption, and survival after the reviewer leaves are settings. A lost key with no editor copy is recorded as a failed delivery, and the review can be resubmitted. It is not reconstructed from nothing.

Ciphertext uses a documented authenticated encryption scheme. The scheme is named in the policy. The default names age or AES-GCM, implementation’s choice, recorded on the review.

A private review repository, when that path is chosen, is owned by the venue. Access is granted and revoked by events. If it disappears, the public hash remains, and the loss is an event. The desk does not pretend the body is still there.

## IRB

IRB is a workflow, not a warning on someone else’s form. A protocol is a matter: drafted, submitted, under-review, approved, refused, amendment, renewed, expired, closed. Evidence is the protocol hash, the approval identifier, `approved_on`, `expires_on`, and the population. Amendments and renewals append. An approval is not edited into the past.

A study, a paper, or a dataset that declares human subjects links to an IRB matter. G1 is on by default. Collection, and a public mount of human-subjects data, wait on an approval dated before collection. The investigator records the approval they were given. The desk does not sit as the IRB of record unless the container is itself that IRB, in which case the IRB chair’s assessment is the approval event.

Who clears the gate is the linked IRB matter in the approved, renewed, or amendment state. There is no anonymous override. An exemption is a state on the IRB matter, with the exemption recorded, and it satisfies G1 when the container allows exemptions. The default allows an exemption only if the IRB matter says exempt.

## Storage and mounts

Git holds records, events, and small artifacts. Bytes that do not fit, or that the container chooses not to store in git, are mounted. A mount is a pointer: hash, size, store, and the external identifier. The default store is Zenodo through Misty, so the mount has a DOI and a Tok stamp. Another provenance-bearing store is a setting. A mount without a hash and a provenance record is not a completed submission.

Replication datasets, high-resolution posters, and supplementary archives follow this rule. The issue attaches the file when it fits. When it does not, the workflow deposits through Misty and the issue carries the DOI. Git LFS is not the default, and not required. The dashboard resolves the mount. The provenance of the bytes is the mount’s DOI and stamp, not the git blob.

## Identifiers

Three dates stay distinct. Tok is existence. The publication date of the author’s version 1 is public priority. A patent filing date is legal priority. A venue decision is none of these.

DOI kinds are named, so implementers do not invent relationships.

- Concept DOI. The work. First publish.
- Version DOI. A dated snapshot under that concept. `newversion`, never a second concept for the same work.
- Reserved DOI. A Zenodo promise. It does not resolve, and it carries no priority, until publish.
- External DOI. A publisher’s identifier, recorded, never fabricated. Related, not a `newversion` of the author’s concept.
- Related DOI. `isPartOf`, `isSupplementTo`, `isReviewOf`, `isVersionOf`, `isPreviousVersionOf`, `isPreprintOf`. The relation is a field. The default for a review is `isReviewOf` unless the container chose “review is a version.”

An ISBN is assigned from a block the publisher holds. It is not fetched from Amazon and not minted from nothing. Amazon, Kaggle, and a proceedings site are outlets. An ASIN is stored beside the DOI. An outlet failure does not unmint.

## Submission, withdrawal, appeal, transfer

An author creates their own DOI, then submits it for inclusion by opening an issue while logged in. The issue carries the identifier and the attachment or the mount. Anonymous submission is off by default. When on, it uses the same salt or ciphertext as blind review.

Withdrawal is an event. Default: the author may withdraw before acceptance. After acceptance, withdrawal needs the editor as well. A venue may withdraw its inclusion. Withdrawal ends the venue matter’s active state. It does not touch the author’s DOI. A withdrawn matter may be resubmitted to the same venue as a new matter linked to the same work, if policy allows. The default allows it.

Appeal is a matter linked to the decision: requested, under-review, upheld, denied. Default decider is an editor who did not make the appealed decision, or the chair. Upholding appends an assessment. It does not edit the earlier one.

The same work at two venues is two matters. Venue A’s rejection is a row on the docket. Venue B’s submission is another row, linked by the author’s DOI or the file hash.

## Notifications and outlets

Notification generation is part of the desk. Delivery is an adapter. GitHub assignment and review requests are the default delivery. Email is optional, and required only for the path that mails a decryption key. A failed delivery is an event, not a silent loss.

An outlet implements prepare, validate, push, record external id, record failure. Zenodo through Misty is the default outlet for a mint and for a mount. Amazon and Kaggle are further adapters. What each accepts is a setting.

## Sessions

Floor plans, registration, visa letters, and hotels are set aside. Sessions and tracks are not. A session has a track, a chair, a start, an end, and a room label. A presentation points at a paper whose latest assessment is accept, with talk or poster, duration, order, and presenter. A later assessment can take it off the program without removing the record. Camera-ready follows the priority switch. Proceedings publish in one action when the container is the proceedings.

## Dashboards

Status comes from the regenerable index and from the public API or GitHub Pages. The signed-in account chooses the face. An author sees their issues, including a reject. A reviewer sees assignments, blinded to the hash when blind is on. A chair sees the queue and the accepted set. An IRB member sees the protocols assigned to them. A reader sees live DOIs. The author’s docket reads the public indexes. The venue may offer the row back.

## Intellectual property

Not created by Misty. Copyright exists on fixation. States: fixed, stamped, optionally registered, licensed, assigned. A patent uses the existing track: drafting, disclosed, filed, published, office-action, granted, abandoned. Filing is counsel’s act. Public outlets wait on `filed_on` and an application number, or on defensive publication. A trademark has a mark, a Nice class, a specimen hash, a filing number, and a renewal date. A design right has the same shape as a patent, with representations instead of claims. A trade secret is sealed locally. Disclosure ends it.

## Books

A book is both a container and an artifact. The container holds chapter matters, editor, contributor roles, order, inclusion and exclusion events, edition, and a table of contents derived from the included chapters. The artifact is the mounted or minted book, with its DOI and its ISBN if a number was assigned. Front matter and back matter are chapters of those kinds. Order is significant and versioned.

## Failure and recovery

Git history remains authoritative if the API, Actions, or Pages fails. A failed workflow retries and records the failure. A merge conflict is a failed transition, not a merged guess. A deleted issue does not delete the matter. The matter records the disappearance. Repository transfer and archival are events. Account suspension removes the login link. It does not delete the person.

A mirror of the repository is a configurable option, off by default. Zenodo being unavailable blocks a mint and a mount. It does not block recording a decision. A corrupted repository is restored from the mirror if one exists, or from the forge’s own recovery. The desk does not invent a second history.

## Security

Secrets never committed, never indexed, never logged, never pasted into an issue. Least privilege follows the permission file. Key revocation is an event. A compromised key is rotated. Secret scanning runs before a public commit. An accidental disclosure is an event, and a public disclosure cannot be made secret again. The response is a notice, a new version, and a record of what was exposed.

## Default switches

`priority = on-accept`. `reviews = closed`. Blind off. Blind arrival, when enabled, is one or more of salted issue, ciphertext, private review repository, and the keyless Tok registry. Review-as-version off, so a review is `isReviewOf` unless the container says it is a version. Retraction-on-later-reject off. Co-author click-accept off. Conflict matching manual. IRB gate on for human subjects. Dataset mount through Misty to Zenodo when the file does not fit in git. Rebuttal rounds uncapped. Registration, invitation letters, and visa letters off. Policy changes apply forward only.

These switches are not on the launch form. They sit beside the workflow. One command still launches a journal, a book, or a conference, with the first issue or the chapter slots or the tracks, and the reserved DOI.

## Set aside

Floor plans and hotels. An ISBN minted from nothing. A patent, trademark, copyright, or IRB approval filed or granted by script. A publisher DOI invented by the desk. A trade secret in the forge. Optional paths on the default launch form. Building the desk on private repositories. A hard cap on review rounds. A hard-wired role. A hard-wired blind path. A hard-wired exclusion of registration or invitation letters.

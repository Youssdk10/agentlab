# AI Code Review Checklist

Rule: AI-written code is a draft from a fast, confident, sometimes wrong
collaborator. Nothing gets committed until it passes every step below.

## 1. Before running anything

- [ ] I know what the code is supposed to do, in one sentence, before reading it.
- [ ] I read it all and understand what it does *before* running it.
      Why: if you don't know what generated code does, pause before running it.
- [ ] No destructive or surprising calls (file deletes, `subprocess`, `os.system`,
      network writes, `eval`/`exec`) that I did not ask for.

## 2. Explain every line

- [ ] I can explain every line in my own words (or I looked it up until I can).
- [ ] I can say why each import is there, and that each imported name really exists.
      Why: the model "fixed" `chainmap` with a reinstall-Python suggestion
      instead of noticing the real name is `ChainMap`.
- [ ] Anything the AI *explained* (not just coded) is checked against the official
      docs, since its reasoning can be wrong even when its claim is right
      (e.g. the wrong reason given for why tuples are faster than lists).

## 3. Run the tools

- [ ] `ruff check .` passes (no unused imports, undefined names, bug patterns).
- [ ] `ruff format .` applied.
- [ ] Security rules pass: `ruff check --select S .`
      (catches things like Flask `debug=True`, SQL built from strings, hardcoded secrets).
- [ ] Type hints present on public functions; docstring has a one-line summary first.
      Why: the generated docstring skipped the summary line.

## 4. Test it (never trust "looks right")

- [ ] Existing tests still pass: `pytest`.
- [ ] I wrote or ran tests for the new behavior, and I saw them **fail first**
      when the feature was missing (so I know they test the right thing).
- [ ] Edge cases tried: empty input, `None`, wrong type, zero/negative, huge input,
      duplicates, inputs that match more than one rule.
      Why: FizzBuzz checked 3 and 5 *before* 15, so 15 returned "fizz"; the
      dict version printed "fizzbuzzfizz buzz" for 15. Both ran fine without crashing.
- [ ] If the AI wrote the tests, I checked they don't just mirror its own bugs.
- [ ] I tested real behavior against a live API or database where possible,
      not only mocks.

## 5. Look for plausible-but-wrong patterns

- [ ] Logic order, off-by-one, and boundary conditions checked by hand.
- [ ] Hidden assumptions flagged (table names, column names, defaults, units,
      encodings, time zones, "a year is 365 days").
      Why: Copilot's SQL guessed the schema; its `age()` divides days by 365.
- [ ] Error handling exists for the realistic failures (network, missing file,
      bad input), not just the happy path.
- [ ] Return types are consistent (not sometimes `None`, sometimes a number,
      sometimes a tuple).
- [ ] It does what I asked and no more (Copilot jumped ahead of the tests in TDD).

## 6. Security, secrets, and licensing

- [ ] No API keys, tokens, or passwords in code, commits, or prompts.
      Secrets come from environment variables or a secrets manager.
- [ ] No unsafe defaults (`debug=True`, `shell=True`, disabled TLS checks,
      string-formatted SQL; use parameterized queries).
- [ ] Anything that looks famous or oddly polished (a classic algorithm with a
      license header) is searched for, in case it was copied from licensed code.
- [ ] I'm not pasting private or employer code into an AI tool I haven't been
      approved to use.

## 7. Readability and maintainability

- [ ] I'd be comfortable maintaining this in six months.
- [ ] A clearer, simpler version was considered. Clever one-liners and nested
      conditional expressions are rewritten.
- [ ] Naming, style, and structure match the rest of my repo.
- [ ] Imports at top of file, explicit encodings when opening text files.

## 8. Before commit

- [ ] I edited the AI output myself instead of accepting it wholesale.
- [ ] Commit message says what the AI produced and what I changed or fixed.
- [ ] I could re-derive or re-write this without the AI if I had to.
      (Overreliance undermines the learning this study plan exists for.)

## Prompting habits that reduce bad output

- Be specific; give context, constraints, and an example of the output you want.
- Ask it to reason step by step, or to write its own solution *before* judging mine.
- Ask for sources or doc links, then open them and confirm.
- Long chats drift; restart with a clean, restated prompt when quality drops.

## Failure log (add a line every time AI code burns me)

| Date | What the AI got wrong | Check that would have caught it | Added to list? |
|------|-----------------------|---------------------------------|----------------|
|      |                       |                                 |                |
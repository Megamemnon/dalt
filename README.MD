# DALT
Copyright (c) 2022 Brian ODell

## Why the world needs another Proof Assistant

Most proof assistants have a steep learning curve and require a significant effort before the user is able to start actually doing anything valuable (like proving something). A noteable exception is Metamath which has a rather low learning curve but in exchange requires elaboration on minutiae ad absurdum.  

DALT enables one to work with a human readable file that resembles a proof with formula appearing on the right and justification (such as axiom references) appearing on the left. DALT also uses Unicode, so all mathematic and logic symbols are a single character and no encodings are visible in the raw text.

The DALT proof strategy is to add formula to your proof from earlier postulated or proven formula and to transform a formula by applying an earlier postulated or proven formula to a statements in your proof. At this high level, it doesn't sound much different than how proofs are expected to work with pen and paper. See the Language section of this document for more detail.

After writing up a Theory in a DALT file, you run the DALT application to validate the theory. Application output is also in the form of a DALT file and comments are included describing any found problems.

After loading and validating your Theory file, DALT provides a REPL prompt where you can test transforming formula by applying Definitions, Axioms, Lemmas, and Theorems.

### Metamath
DALT is heavily inspired by [Metamath](https://metamath.org) and even supports most Metamath proofs directly (as shown on the Metamath web pages, not as entered into a Metamath *.mm files). DALTs sole power, like Metamath, is substitution. The differences from Metamath are:  

1. DALT files are formatted similarly to proofs.  
2. DALT uses unicode Greek characters and mathematical symbols.
3. Running a DALT file through the DALT application produces a replacement DALT files with comments on any existing errors.  

## Language

The example file projcalculus.dalt, included with this package, defines the basic Axioms of Propositional Calculus and proves several Lemmas and Theorems up through Minimal Implicational Calculus, a single axiom identified by C.A. Meredith. [See Metamath's minimp page](https://us.metamath.org/mpeuni/mmtheorems18.html#mm1730s) for additional information. 

To begin a DALT file, you should name your Theory, using the THEORY keyword.

<pre>
THEORY Propositional Calculus
</pre>

Any line that begins with '#' is a comment and ignored by the interpreter. Whole line comments are the only type of comment supported by DALT.

### Definitions and Axioms

Use the DEF keyword to introduce a Definition and the AXIOM keyword to introduce an Axiom. Note the double dash and space ("-- ") identifies the beginning of the formula for the interpreter.
<pre>
DEF Phi                     -- φ  
DEF Psi                     -- ψ  

AXIOM ax-1                  -- φ→(ψ→φ)  
AXIOM ax-2                  -- φ→(ψ→χ)→((φ→ψ)→(φ→χ))  
AXIOM ax-3                  -- ((¬φ)→(¬ψ))→(ψ→φ)  
AXIOM ax-mp                 -- ψ  
  HYPOTHESIS                -- φ  
  HYPOTHESIS                -- φ→ψ  
</pre>
AXIOM statements may be followed by one or more HYPOTHESIS statements. These statements should be indented. When an Axiom is used in a Lemma or Theorem, each Hypothesis for the Axiom must be fulfilled. This is described in the following section.

### Lemmas and Theorems

Lemmas and Theorems are treated identically by the interpreter. It's up to you to decide what you want to use Lemmas for or if you simply always want to use Theorems.

A Lemma or Theorem begins with an identifying line and is followed by a proof. All proofs end with QED, which tells the interpreter the proof is finished.

<pre>
LEMMA a1i                   -- (ψ→φ)  
  HYPOTHESIS                -- φ  
  AXIOM ax-1                -- φ→(ψ→φ)  
  AXIOM ax-mp 1 2           -- (ψ→φ)  
  QED  
</pre>

Let's examine the above Lemma line by line:  

1. The LEMMA keyword begins the Lemma introcutory line. The Lemma's name is "a1i" and the Assertion is (ψ→φ).  
2. The proof begins with a Hypothesis which is simply Phi. The hypothesis will need to be provided by any subsequent Lemma or Theorem which uses "a1i". Basically, if you want to use "a1i", you have to specify what Phi is. The variables in (ψ→φ) are placeholders and the value you provide for Phi will be used. Psi ψ will be introduced as an antecendent (and this is the entire purpose of the Lemma "a1i", to introduce an antecedent and implication).  
3. Axiom ax-1 is added to the statements in the proof of "a1i". Axiom ax-1 has no hypothesis, so the formula on the right side of this line is simply ax-1 verbatim, however, variable substitutions could be made (by YOU manually) and the interpreter would confirm the formula you provided is equivalent to ax-1.  
4. The Axiom Modus Ponens is applied. This Axiom has two Hypothesises and the "1 2" on this line indicates the interpreter should use the 1st statement in the current proof to satisfy Hypothesis 1 and the 2nd statement in the current proof to satisfy Hypothesis 2. ax-1's first Hypothesis is simply Phi; this proof says use Phi; simple enough. But ax-1's second Hypothesis is Psi implies Phi φ→ψ and this proof says use φ→(ψ→φ). The interpreter will Unify these to statements and determine the Axiom's Psi is equivalent to the proof's ψ→φ. So, the formula on the right side of this line must be ψ→φ, otherwise the interpreter would identify in an error.
5. QED notifies the interpreter the proof is finished. The interpreter verifies the Assertion is equal to the final statement in the proof and stores it in the appropriate dictionary for future use.

#### Proof Commands
##### HYPOTHESIS
Enables the manual entry of a statement, which is not supported by a prior Assertion.  
##### DEF|AXIOM|LEMMA|THEOREM
Adds a Definition, Axiom, Lemma, or Theorem to the proof steps.  
If the named Assertion includes one or more Hypothesises, you must identify prior proof steps by number to satisfy those Hypothesises in the order in which they occur. Those identified proof steps are unified with the Hypothesises of the named element and the identified Assertion is transformed using the same variable substitutions and added to the Proof Steps.  
##### SUBTERM DEF|AXIOM|LEMMA|THEOREM
Like DEF|AXIOM|LEMMA|THEOREM but only prior Assertions with a single Hypothesis may be used. A Subterm in the prior Proof Step, identified by number, is unified with the named Assertion's Hypothesis and the named Assertion is transformed with the same variable substitutions, replacing the Subterm. You provide the final statement; the system will verify your statement is a valid transformation of the prior Proof Step by cycling through its terms and making substitutions. Only one Subterm can be modified in this fashion. If multiple Subterms need to be transformed, multiple applications of this proof command are required.
##### QED
Concludes the proof; system will verify the final proof step matches the Assertion and then add the Lemma/Theorem to the appropriate dictionary.  
##### QEDBY DEF|AXIOM|LEMMA|THEOREM
Concludes the proof by confirming the final proof step matches the identified Definition, Axiom, Lemma, or Theorem. The system will then verify the final proof step matches the Assertion and then add the Lemma/Theorem to the appropriate dictionary.  
### Mathematical Symbols
∀ U2200, ∃ U2203, ∄ U2204, − U2212, and ¬ U00AC are all left-associative Unary Operators.  
+, -, × U00D7, /, ^, ∧ U2227, ∨ U2228, ',', ∘ U2218, :, ∈ U2208, ⊂ U2282, ⊆ U2286 are left associative Binary Operators.  
→ U2192, ↔ U2194, =, ≠ U2260 are Connectives, a type of (yes, left associative) Binary Operator with high precedence. Connectives are identified as such to avoid the need to prioritize them with parenthesis.  
Open '(' and Close ')' Parenthesis are required to establish operator precendence.  

See the Compose section for an .XCompose file and instructions on using a Compose key with custom Compose options.  

### Greek and Latin Letters
All uppercase Greek (Α to Ω (U0391 to U03A9)) and Latin (A to Z) characters are Constants.  
All lowercase Greek (α to ω (U03B1 to U03C9)) and Latin (a to z) characters are Variables.  

See the Compose section for an .XCompose file and instructions on using a Compose key with custom Compose options.  

## REPL

After DALT completes loading/validating a Theory file, it presents a read-eval-print loop where you can test formula transformations using the following commands.

### l or list

Lists formula you've entered thus far.
<pre>
]l
1: a
2: a→(b→a)
3: b→a
</pre>

### c or clear

Clears the list.

### h or hypothesis

Enter a formula to append to the list.

<pre>
]h a
]h a→(b→a)
</pre>

### d or definition, a or axiom, l or lemma, t or theorem

Add a Definition, Axiom, Lemma, or Theorem to the list. If the identified formula contains one or more Hypothesis, indicate formulas already in the list to satisfy these Hypothesis and the named formula will be transformed based on Unification with your Hypothesis.

<pre>
]l
1: a
2: a→(b→a)
]a ax-mp 1 2
]l
1: a
2: a→(b→a)
3: b→a
</pre>

### s or subterm

TODO

### exit
Quit DALT.

## Compose

Linux users (and others, but I don't have instructions for other OSs) can enable a Compose key on their keyboard and use a custom Compose file to simplify entering unicode characters. The file .XCompose in this project is my own custom Compose file placed in my Home folder. This file includes my system's Compose file and adds new Compose options supporting all of the Unicode characters needed by DALT. The .XCompose file indicates the key combinations for each character.

In this example from .XCompose, Multi_Key refers to your Compose key (I use the right ALT key). So if I type right-ALT, let go of that key and then type the MINUS (-) key and then GREATER (>) key the implies character (right arrow, →) is inserted. 
<pre>
&lt;Multi_key&gt; &lt;minus&gt; &lt;greater&gt; : "→"
</pre>

This is much simpler then remembering Unicode numbers and fewer key clicks, too.

If you run Gnome, you can select and enable a Compose key in Settings. For other desktops, it's likely similar but you may have to use Google. 
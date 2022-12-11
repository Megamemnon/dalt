# dalt - define axiom lemma theorem
# Copyright (c) 2022 Brian O'Dell

import enum, sys

DEBUG=True
COLWIDTH=30
DEFAULTTHEORYFILE='propcalculus.dalt'
theoryfile=''

ANSIESC='\033'
RESET=ANSIESC+'[0m'
VIOLET=ANSIESC+'[38;5;91m'
BLUE=ANSIESC+'[38;5;33m'
TEAL=ANSIESC+'[38;5;87m'
GREEN=ANSIESC+'[38;5;47m'
YELLOW=ANSIESC+'[38;5;228m'
ORANGE=ANSIESC+'[38;5;222m'
RED=ANSIESC+'[38;5;160m'
PINK=ANSIESC+'[38;5;206m'


LANGUAGE={'unary operators':['∀','∃','∄','−','¬'],
  'binary operators':['+','-','×','/','^','∧','∨',',','∘',':','∈','⊂','⊆'],
  'parens':['()'],
  'listmarkers':['[]'],
  'connectives':['→','↔','=','≠']}

class CharacterType(enum.Enum):
  symbol=1
  greekLower=2
  greekUpper=3
  latinLower=4
  latinUpper=5
  digit=6

class TokenType(enum.Enum):
  binop=1
  unop=2
  atom=3
  variable=4
  parenopen=5
  parenclose=6
  connective=7
  listmarkeropen=8
  listmarkerclose=9
  parens=10
  listmarker=11

class ASTNode():
  def __init__(self, nodetype, symbol, left, right, uniqueid):
    self.nodetype=nodetype
    self.symbol=symbol
    self.left=left
    self.right=right
    self.uniqueid=uniqueid

  def getFormula(self, paren=True):
    f=''
    match self.nodetype:
      case TokenType.unop:
        f+=self.symbol
        f+=self.left .getFormula()
      case TokenType.binop:
        if paren:
          f+='('
        f+=self.left .getFormula()
        f+=self.symbol
        f+=self.right .getFormula()
        if paren:
          f+=')'
      case TokenType.atom | TokenType.variable:
        f+=self.symbol
      case TokenType.listmarker:
        f+=self.symbol[0]
        f+=self.right.getFormula(False)
        f+=self.symbol[1]
      case TokenType.connective:
        if paren:
          f+='('
        f+=self.left .getFormula()
        f+=self.symbol
        f+=self.right .getFormula()
        if paren:
          f+=')'
    return f

  def equivalent(self, astnode):
    l=True
    r=True
    if self.nodetype==TokenType.variable:
      return True
    if astnode.nodetype!=self.nodetype:
      return False
    if astnode.symbol!=self.symbol: # and self.nodetype!=TokenType.variable:
      return False
    if self.left:
      if not astnode.left:
        return False
      else:
        l=self.left.equivalent(astnode.left)
    else:
      if astnode.left:
        return False
    if self.right:
      if not astnode.right:
        return False
      else:
        r=self.right.equivalent(astnode.right)
    else:
      if astnode.right:
        return False
    return l and r      

  def unify(self, astnode):
    if self.nodetype==TokenType.variable:
      return [(astnode,self)]
    l=[]
    r=[]
    if astnode.nodetype!=self.nodetype:
      return None
    if self.left is not None:
      if astnode.left is None:
        return None
      l=self.left.unify(astnode.left)
    elif astnode.left is not None:
      return None
    if self.right is not None:
      if astnode.right is None:
        return None
      r=self.right.unify(astnode.right)
    elif astnode.right is not None:
      return None
    if l is None and r is None:
      return None
    unifier=[]
    if type(l)==list:
      unifier.extend(l)
    if type(r)==list:
      unifier.extend(r)
    return unifier

def getUnifierString(unifier):
  u='{'
  for c,var in enumerate(unifier):
    u+=var[0].getFormula(False)+'|'+var[1].getFormula(False)
    if c!=len(unifier)-1:
      u+=','
  u+='}'
  return u

def getUnifierErrors(unifier):
  uerrors=[]
  uclean=[]
  for u in unifier:
    if len(uclean)==0:
      uclean.append(u)
    else:
      found=False
      u1=u[1].getFormula(False)
      u0=u[0].getFormula(False)
      for uc in uclean:
        uc1=uc[1].getFormula(False)
        uc0=uc[0].getFormula(False)
        if u1==uc1 and u0!=uc0:
          uerrors.append(u)
          uerrors.append(uc)
          found=True
      if not found:
        uclean.append(u)
  uclean=[]
  for ue in uerrors:
    if len(uclean)==0:
      uclean.append(ue)
    else:
      ue1=ue[1].getFormula(False)
      ue0=ue[0].getFormula(False)
      for uc in uclean:
        uc1=uc[1].getFormula(False)
        uc0=uc[0].getFormula(False)
        if ue1==uc1 and ue0!=uc0:
          uclean.append(ue)
  return uclean

def getCharacterType(glyph):
  symbols=[chr(unicode) for unicode in list(range(ord('∀'),ord('⋿')+1))]
  symbols.extend(['→','↔','¬','≠','×'])
  symbols.extend([chr(unicode) for unicode in list(range(ord('!'),ord('/')+1))])
  symbols.extend([chr(unicode) for unicode in list(range(ord(':'),ord('@')+1))])
  symbols.extend([chr(unicode) for unicode in list(range(ord('['),ord('`')+1))])
  symbols.extend([chr(unicode) for unicode in list(range(ord('{'),ord('~')+1))])
  digit=[chr(unicode) for unicode in list(range(ord('0'),ord('9')+1))]
  greekUpper=[chr(unicode) for unicode in list(range(ord('Α'),ord('Ω')+1))]
  greekLower=[chr(unicode) for unicode in list(range(ord('α'),ord('ω')+1))]
  latinUpper=[chr(unicode) for unicode in list(range(ord('A'),ord('Z')+1))]
  latinLower=[chr(unicode) for unicode in list(range(ord('a'),ord('z')+1))]
  if glyph in ['∅']:
    return CharacterType.digit
  if glyph in symbols:
    return CharacterType.symbol
  if glyph in digit:
    return CharacterType.digit    
  if glyph in greekLower:
    return CharacterType.greekLower
  if glyph in greekUpper:
    return CharacterType.greekUpper
  if glyph in latinLower:
    return CharacterType.latinLower
  if glyph in latinUpper:
    return CharacterType.latinUpper
  return None

def isIdentifierCharacter(glyph):
  gtype=getCharacterType(glyph)
  if gtype is not None \
    and gtype!=CharacterType.symbol:
    return True
  return False

def getTokenType(token, language):
  t=getCharacterType(token)
  if t==CharacterType.symbol:
    if token in language['unary operators']:
      return TokenType.unop
    if token in language['binary operators']:
      return TokenType.binop
    for enc in language['parens']:
      if token==enc[0]:
        return TokenType.parenopen
      if token==enc[1]:
        return TokenType.parenclose
    for enc in language['listmarkers']:
      if token==enc[0]:
        return TokenType.listmarkeropen
      if token==enc[1]:
        return TokenType.listmarkerclose
    if token in language['connectives']:
      return TokenType.connective
  else:
    if t==CharacterType.greekLower or t==CharacterType.latinLower:
      return TokenType.variable
    if t==CharacterType.greekUpper or t==CharacterType.latinUpper:
      return TokenType.atom
    if t==CharacterType.digit:
      return TokenType.atom
  return None

def getMatchingParenOpen(parenclose, language):
  for x in language['parens']:
    if x[1]==parenclose:
      return x[0]
  return None

def getMatchingListMarkerOpen(listmarkerclose, language):
  for x in language['listmarkers']:
    if x[1]==listmarkerclose:
      return x[0]
  return None

def formulaToAST(formula, language):

  def parse1(formula, language):
    opstack=[]
    postfix=[]
    lp=language['parens'][0][0]
    rp=language['parens'][0][1]
    astroot=None
    findex=0
    while findex<len(formula):
      c=formula[findex]
    # for c in formula:
      t=getTokenType(c, language)
      c1=''
      if t==TokenType.atom or t==TokenType.variable:
        while isIdentifierCharacter(c):
          postfix.append(c)
          if findex+1<len(formula):
            findex+=1
            c=formula[findex]
          else:
            break
        postfix.append(' ')
        t=getTokenType(c, language)
      if t==TokenType.parenopen or t==TokenType.listmarkeropen:
        postfix.append(c)
      if t==TokenType.parenopen:
        opstack.append(c)
      if t==TokenType.parenclose:
        c1=opstack.pop()
        while c1!=lp:
          postfix.append(c1)
          c1=opstack.pop()
        postfix.append(c)
      if t==TokenType.listmarkeropen:
        opstack.append(c)
      if t==TokenType.listmarkerclose:
        eo=getMatchingListMarkerOpen(c, language)
        c1=opstack.pop()
        while c1!=eo:
          postfix.append(c1)
          c1=opstack.pop()
        postfix.append(c)
      if t==TokenType.connective or t==TokenType.binop:
        if len(opstack)>0:
          c1=opstack.pop()
          if c1!=lp and getTokenType(c1, language)!=TokenType.listmarkeropen:
            postfix.append(c1)
          else:
            opstack.append(c1)
        opstack.append(c)
      if t==TokenType.unop:
        opstack.append(c)
      findex+=1
    while len(opstack)>0:
      postfix.append(opstack.pop())
    return postfix

  def parse2(postfix, language):
    id=1
    output=[]
    connectivestack=[]
    node=None
    lp=language['parens'][0][0]
    rp=language['parens'][0][1]
    pfindex=0
    while pfindex<len(postfix):
      c=postfix[pfindex]
    # for c in postfix:
      t=getTokenType(c, language)
      if t==TokenType.atom or t==TokenType.variable:
        identifier=''
        while isIdentifierCharacter(c):
          identifier+=c
          if pfindex+1<len(postfix):
            pfindex+=1
            c=postfix[pfindex]
          else:
            break
        node=ASTNode(t, identifier, None, None, id)
        id+=1
        output.append(node)
        t=getTokenType(c, language)
      if t==TokenType.listmarkeropen:
        output.append(c)
      if t==TokenType.binop or t==TokenType.connective:
        right=output.pop()
        left=output.pop()
        node=ASTNode(t, c, left, right, id)
        id+=1
        output.append(node)
      if t==TokenType.listmarkeropen:
        node=ASTNode(TokenType.listmarker, language['listmarkers'][0], None, None, id)
        id+=1
        connectivestack.append(node)
      if t==TokenType.listmarkerclose:
        tmpstack=[]
        lmo=getMatchingListMarkerOpen(c, language)
        right=output.pop()
        while right!=lmo:
          if len(connectivestack)!=0:
            node=connectivestack.pop()
            node.right=right
            tmpstack.append(node)
          right=output.pop()
        output.extend(tmpstack)
      if t==TokenType.unop:
        left=output.pop()
        node=ASTNode(t, c, left, None, id)
        id+=1
        output.append(node)
      pfindex+=1
    # Should never have leftovers on the connectivesstack
    while len(connectivestack)!=0:
      right=output.pop()
      node=connectivestack.pop()
      node.right=right
      output.append(node)
    return output

  try:
    return parse2(parse1(formula, language), language)[0]
  except:
    print(f'# {RED}ERROR{RESET} Unable to parse {formula}')
    return None

def colorizeFormula(formula):
  paren=0
  newformula=''
  colors=[BLUE, PINK, TEAL, VIOLET]
  for c in formula:
    if c=='(':
      paren+=1
      color=colors[paren%4]
      newformula+=color+c+RESET
    elif c==')':
      newformula+=color+c+RESET
      paren-=1
      color=colors[paren%4]
    elif c in ['→','↔','=','≠','∀','∃','∄','∧','∨','∘']:
      newformula+=YELLOW+c+RESET
    else:
      newformula+=c
  return newformula

def loadTheory(filename, language):
  f=open(filename,'r')
  if not f:
    return False
  lines=f.readlines()
  f.close()
  theoryName=''
  theory={}
  theory['DEFS']={}
  theory['AXIOMS']={}
  theory['LEMMAS']={}
  theory['THEOREMS']={}
  postulatename=''
  postulateformula=''
  postulateast=None
  formulaname=''
  formula=''
  formulaast=None
  theoremname=''
  theoremformula=''
  theoremast=None

  i=0
  while i<len(lines):
    line=lines[i].strip()
    # if line[-1]=='\n':
    #   line=line[:-1]
    if len(line)==0:
      print()
      i+=1
      continue
    l=line.split()
    dashes=line.find('--')
    match l[0]:
      case 'THEORY':
        theoryName=line[7:]
        print(f'{PINK}{l[0]}{RESET} {theoryName}')
      case 'DEF'|'AXIOM':
        postulatename=line[len(l[0])+1:dashes].replace('\t','').strip()
        postulateformula=line[dashes+2:].replace('\t','').strip()
        postulateast=formulaToAST(postulateformula, language)
        if postulateast is None:
          continue
        postulateformula=postulateast.getFormula(False)
        print(f'{PINK}{l[0]}{RESET} {postulatename}{chr(0x20)*(COLWIDTH-(len(l[0])+len(postulatename)+1))}-- {colorizeFormula(postulateformula)}')
        if l[0]=='AXIOM':
          hypothesises=[]
          if i+1<len(lines):
            i+=1
            if len(lines[i].strip().split())==0:
              continue
            while lines[i].strip().split()[0]=='HYPOTHESIS':
              dashes=lines[i].find('--')
              formula=lines[i][dashes+2:].replace('\t','').strip()
              formulaast=formulaToAST(formula, language)
              formula=formulaast.getFormula(False)
              hypothesises.append(['HYPOTHESIS',formula])
              print(f'  {TEAL}HYPOTHESIS{RESET}{chr(0x20)*(COLWIDTH-12)}-- {colorizeFormula(formula)}')
              if i+1<len(lines):
                i+=1
              else:
                break
              if len(lines[i].strip().split())==0:
                break
            i-=1
          if len(hypothesises)==0:
            theory[l[0]+'S'][postulatename]=[postulateformula]
          else:
            theory[l[0]+'S'][postulatename]=[postulateformula, hypothesises]
        else:
          theory[l[0]+'S'][postulatename]=[postulateformula]
      case 'LEMMA'|'THEOREM':
        theoremname=line[len(l[0])+1:dashes].replace('\t','').strip()
        theoremformula=line[dashes+2:].replace('\t','').strip()
        theoremast=formulaToAST(theoremformula, language)
        if theoremast is None:
          continue
        theoremformula=theoremast.getFormula(False)
        print(f'{PINK}{l[0]}{RESET} {theoremname}{chr(0x20)*(COLWIDTH-(len(l[0])+len(theoremname)+1))}-- {colorizeFormula(theoremformula)}')
        prooftype=l[0]+'S'
        step=-1
        proofsteps=[]
        while lines[i].strip()[:3]!='QED':
          i+=1
          if i>=len(lines):
            print(f'# {RED}ERROR{RESET} Expected QED')
            break
          step+=1
          tline=lines[i].strip()
          if len(tline)==0:
            print()
            i+=1
            continue
          t=tline.split()
          dashes=tline.find('--')
          match t[0]:
            case 'HYPOTHESIS':
              formula=tline[dashes+2:].replace('\t','').strip()
              formulaast=formulaToAST(formula, language)
              if formulaast is None:
                continue
              formula=formulaast.getFormula(False)
              print(f'  {TEAL}{t[0]}{RESET}{chr(0x20)*(COLWIDTH-(len(t[0])+2))}-- {colorizeFormula(formula)}')
              proofsteps.append(['HYPOTHESIS',formula])
            case 'AXIOM'|'DEF'|'LEMMA'|'THEOREM':
              formula=tline[dashes+2:].replace('\t','').strip()
              formulaast=formulaToAST(formula, language)
              if formulaast is None:
                continue
              formula=formulaast.getFormula(False)
              postulatename=t[1]
              if postulatename not in theory[t[0]+'S']:
                print(f'# {RED}ERROR{RESET}:{postulatename} not found in {t[0]}S dictionary')
                continue
              postulateentry=theory[t[0]+'S'][postulatename]
              postulateformula=postulateentry[0]
              postulateast=formulaToAST(postulateformula, language)
              if postulateast is None:
                print(f'# {RED}ERROR{RESET}:{postulatename} {colorizeFormula(postulateformula)} cannot be parsed')
                continue
              postulateformula=postulateast.getFormula(False)
              if not postulateast.equivalent(formulaast):
                print(f'# {RED}ERROR{RESET} provided formula is not equivalent to {formulaname} {colorizeFormula(formula)}')
              if len(postulateentry)>1:
                try:
                  postulatesteps=postulateentry[1]
                  x=tline.find(t[1])+len(t[1])
                  steprefs=tline[x:dashes].split()
                  pstep=0
                  unifier=[]
                  for h in postulatesteps:
                    if h[0]=='HYPOTHESIS':
                      x=int(steprefs[pstep])-1
                      refformula=proofsteps[x][1]
                      refformulaast=formulaToAST(refformula, language)
                      posformulaast=formulaToAST(h[1], language)
                      if not posformulaast.equivalent(refformulaast):
                        print(f'# {RED}ERROR{RESET} proof step {int(steprefs[pstep]-1)} is not equivalent to {h[1]}')
                        continue
                      un=posformulaast.unify(refformulaast)
                      if un is None:
                        print(f'# {RED}ERROR{RESET} {refformula} cannot be unified with {h[1]}')
                        continue
                      unifier.extend(un)
                      pstep+=1
                  unifier.extend(postulateast.unify(formulaast))
                  uerrors=getUnifierErrors(unifier)
                  if uerrors!=[]:
                    ue=getUnifierString(uerrors)
                    print(f'# {RED}ERROR{RESET} Inconsistent Unifiers between Hypothesis(es) and provided Formula: {ue}')
                    continue
                except:
                  print(f'# {RED}ERROR{RESET} Unable to process proof steps for line {tline[:dashes].strip()}')
              proofsteps.append([tline[:dashes].strip(), formula])
              print(f'  {TEAL}{t[0]}{RESET} {tline[len(t[0]):dashes].strip()}{chr(0x20)*(COLWIDTH-(len(t[0])+len(tline[len(t[0]):dashes].strip())+3))}-- {colorizeFormula(formula)}')
            case 'QED':
              print(f'  {TEAL}QED{RESET}')
              if theoremformula!=proofsteps[-1][1]:
                print(f'# {RED}ERROR{RESET} Assertion {theoremformula} is not supported by proof {colorizeFormula(proofsteps[-1][1])}')
              theory[prooftype][theoremname]=[theoremformula, proofsteps]
              pass
            case _:
              if tline[0]!='#':
                print(f'# {tline}')
              else:
                print(tline)
      case _:
        if line[0]!='#':
          print(f'# {line}')
        else:
          print(line)
    i+=1
  return theory

def main():
  global DEBUG, DEFAULTTHEORYFILE, theoryfile
  print(f'{BLUE}Calculus of Calculi 0.1\nCopyright (c) 2022 Brian O\'Dell{RESET}')
  if DEBUG:
    t=DEFAULTTHEORYFILE
  else:
    usage=f'{ORANGE}usage:{sys.argv[0]} language=mylanguage theory=mytheory{RESET}'
    if len(sys.argv)<3:
      print(usage)
      sys.exit(1)
    if sys.argv[1][:9]!='language=':
      print(usage)
      sys.exit(1)
    l=sys.argv[1][9:]
    if sys.argv[2][:7]!='theory=':
      print(usage)
      sys.exit(1)
    t=sys.argv[2][7:]
  theoryfile=t
  loadTheory(theoryfile, LANGUAGE)

if __name__=='__main__':
  main()
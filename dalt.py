# dalt - define axiom lemma theorem
# Copyright (c) 2022 Brian O'Dell

import enum, sys

COLWIDTH=30
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


LANGUAGE={'unary operators':['∀','∃','∄','−','¬','∣','∟','#'],
  'binary operators':['+','-','×','/','^','∧','∨',',','∘',':','∊','⊂','⊆','∩','∪','∥','⊚'],
  'parens':['()'],
  'listmarkers':['[]'],
  'setmarkers':['{}'],
  'connectives':['→','↔','=','≠','≌','|']}

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
  setmarkeropen=12
  setmarkerclose=13
  setmarker=14

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
    for enc in language['setmarkers']:
      if token==enc[0]:
        return TokenType.setmarkeropen
      if token==enc[1]:
        return TokenType.setmarkerclose
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

# def getMatchingParenOpen(parenclose, language):
#   for x in language['parens']:
#     if x[1]==parenclose:
#       return x[0]
#   return None

# def getMatchingListMarkerOpen(listmarkerclose, language):
#   for x in language['listmarkers']:
#     if x[1]==listmarkerclose:
#       return x[0]
#   return None

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
        f+='['
        f+=self.right.getFormula(False)
        f+=']'
      case TokenType.setmarker:
        f+='{'
        f+=self.right.getFormula(False)
        f+='}'
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

  def resolve(self, astnode):
    resolution=[]
    x=self.unify(astnode)
    if x is not None:
      resolution.append([self, x])
    if self.left is not None:
      x=self.left.resolve(astnode)
      if x is not None:
        resolution.extend(x)
    if self.right is not None:
      x=self.right.resolve(astnode)
      if x is not None:
        resolution.extend(x)
    return resolution

  def replaceVariable(self, var, newNode):
    l=False
    r=False
    if self.left is not None:
      if self.left.nodetype==TokenType.variable and self.left.symbol==var:
        self.left=newNode
        l=True
      else:
        l=self.left.replaceVariable(var, newNode)
    if self.right is not None:
      if self.right.nodetype==TokenType.variable and self.right.symbol==var:
        self.right=newNode
        r=True
      else:
        r=self.right.replaceVariable(var, newNode)
    if l or r:
      return True
    return False

  def replaceNode(self, currentNode, newNode):
    if self.left is not None:
      if self.left.uniqueid==currentNode.uniqueid:
        self.left=newNode
        return True
      if self.left.replaceNode(currentNode, newNode)==True:
        return True
    if self.right is not None:
      if self.right.uniqueid==currentNode.uniqueid:
        self.right=newNode
        return True
      if self.right.replaceNode(currentNode, newNode)==True:
        return True
    return False

  def copy(self):
    left=None
    right=None
    if self.left is not None:
      left=self.left.copy()
    if self.right is not None:
      right=self.right.copy()
    return ASTNode(self.nodetype, self.symbol, left, right, self.uniqueid)

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


def getMatchedSubstitutionNodes(formula, substterm, language, reversed=False):
  fnode=formulaToAST(formula, language)
  sterm=formulaToAST(substterm, language)
  if fnode is None or sterm is None:
    return None
  if sterm.nodetype!=TokenType.connective:
    print(f'# {RED}ERROR{RESET} invalid subsitution formula')
    return None
  if reversed:
    fterm=sterm.right
  else:
    fterm=sterm.left
  result=[fnode]
  result.append(fnode.resolve(fterm))
  return result

def substitute(formulaAST, substterm, matchnode, matchunifier, language, reversed=False):
  sterm=formulaToAST(substterm, language)
  if sterm is None:
    return None
  if reversed:
    replacementterm=sterm.left
  else:
    replacementterm=sterm.right
  for tpl in matchunifier:
    if replacementterm.nodetype==TokenType.variable and replacementterm.symbol==tpl[0].symbol:
      replacementterm=tpl[1]
    else:
      replacementterm.replaceVariable(tpl[0].symbol, tpl[1])
  replacementterm.uniqueid=matchnode.uniqueid
  if formulaAST.uniqueid==replacementterm.uniqueid:
    formulaAST=replacementterm
  else:
    formulaAST.replaceNode(matchnode, replacementterm)
  return formulaAST.getFormula(False)

def apply(formula, equality, termtomatch, language, reversed):
  resolution=getMatchedSubstitutionNodes(formula, equality, language, reversed)
  if resolution is None:
    return None
  forumlaAST=resolution[0]
  matchnodesunifiers=resolution[1]
  for c, mnu in enumerate(matchnodesunifiers):
    matchedterm=mnu[0].getFormula(False)
    if matchedterm==termtomatch:
      formula=substitute(forumlaAST, equality, mnu[0], mnu[1], language, reversed)
      return formula

def verifyApplication(formula, equality, userapplied, language):
  userappliedast=formulaToAST(userapplied, language)
  resolutions=getMatchedSubstitutionNodes(formula, equality, language, False)
  if resolutions is None:
    return False
  matchnodesunifiers=resolutions[1]
  for mnu in matchnodesunifiers:
    formulaast=resolutions[0].copy()
    newformula=substitute(formulaast, equality, mnu[0], mnu[1], language, False)
    if newformula==userapplied:
      return True
    newformulaast=formulaToAST(newformula, language)
    if newformulaast is not None and userappliedast is not None:
      if newformulaast.equivalent(userappliedast):
        return True
  return False

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
      if t==TokenType.parenopen or t==TokenType.listmarkeropen or t==TokenType.setmarkeropen:
        postfix.append(c)
        opstack.append(c)
      if t==TokenType.parenclose or t==TokenType.listmarkerclose or t==TokenType.setmarkerclose:
        match t:
          case TokenType.parenclose:
            marker=lp
          case TokenType.listmarkerclose:
            marker='['
          case TokenType.setmarkerclose:
            marker='{'
        c1=opstack.pop()
        while c1!=marker:
          postfix.append(c1)
          c1=opstack.pop()
        postfix.append(c)
      if t==TokenType.connective or t==TokenType.binop:
        if len(opstack)>0:
          c1=opstack.pop()
          if c1!=lp and getTokenType(c1, language)!=TokenType.listmarkeropen \
            and getTokenType(c1, language)!=TokenType.setmarkeropen:
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
      if t==TokenType.binop or t==TokenType.connective:
        right=output.pop()
        left=output.pop()
        node=ASTNode(t, c, left, right, id)
        id+=1
        output.append(node)
      if t==TokenType.unop:
        left=output.pop()
        node=ASTNode(t, c, left, None, id)
        id+=1
        output.append(node)
      if t==TokenType.listmarkeropen or t==TokenType.setmarkeropen:
        match t:
          case TokenType.listmarkeropen:
            markertype=TokenType.listmarker
          case TokenType.setmarkeropen:
            markertype=TokenType.setmarker
        output.append(c)
        node=ASTNode(markertype, c, None, None, id)
        id+=1
        connectivestack.append(node)
      if t==TokenType.listmarkerclose or t==TokenType.setmarkerclose:
        match t:
          case TokenType.listmarkerclose:
            marker='['
          case TokenType.setmarkerclose:
            marker='{'
        tmpstack=[]
        right=output.pop()
        while right!=marker:
          if len(connectivestack)!=0:
            node=connectivestack.pop()
            node.right=right
            tmpstack.append(node)
          right=output.pop()
        output.extend(tmpstack)
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

def confirmInduction(formula1, formula2, formula3, zero, var, svar, language):
  # confirm Induction has occurred by recreating formulas 1 and 3 from formula2 
  # by substituting zero and svar for var, respectively
  # this method still leaves open the possibility of a contrived case 
  # that isn't actually induction - specifically, the zero, var, and svar are not 
  # confirmed to be truly a zero, variable and the variable's successor
  formula1ast=formulaToAST(formula1, language)
  formula2ast=formulaToAST(formula2, language)
  formula3ast=formulaToAST(formula3, language)
  formula1fixd=formula1ast.getFormula(False)
  formula2fixd=formula2ast.getFormula(False)
  formula3fixd=formula3ast.getFormula(False)
  f1ast=formula2ast.copy()
  zeroast=formulaToAST(zero, language)
  f1ast.replaceVariable(var, zeroast)
  f3ast=formula2ast.copy()
  svarast=formulaToAST(svar, language)
  f3ast.replaceVariable(var, svarast)
  f1formula=f1ast.getFormula(False)
  f3formula=f3ast.getFormula(False)
  if f1formula!=formula1fixd:
    print(f'# {RED}ERROR{RESET} First formula should be {colorizeFormula(f1formula)}')
    return False
  if f3formula!=formula3fixd:
    print(f'# {RED}ERROR{RESET} Third formula should be {colorizeFormula(f3formula)}')
    return False
  return True
  # Prior code is insufficient because it only confirms the three formulas are equivalent
  # replacement code above confirms the first and third formulas can be derived from the second formula
  # f2f1=formula2ast.equivalent(formula1ast)
  # f2f3=formula2ast.equivalent(formula3ast)
  # z=zero in formula1
  # v=var in formula2
  # sv=svar in formula3
  # if f2f1 and f2f3 and z and v and sv:
  #   return True
  # return False

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
  while i<len(lines)-1:
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
            if len(lines[i].strip().split())!=0:
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
                print(f'# {RED}ERROR{RESET} transformed formula {colorizeFormula(postulateformula)} is not equivalent to {formulaname} {colorizeFormula(formula)}')
              if len(postulateentry)>1:
                postulatesteps=postulateentry[1]
                if postulatesteps[-1][0]!='QEDBY':
                  try:
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
                          print(f'# {RED}ERROR{RESET} proof step {int(steprefs[pstep])} is not equivalent to {colorizeFormula(h[1])}')
                          continue
                        un=posformulaast.unify(refformulaast)
                        if un is None:
                          print(f'# {RED}ERROR{RESET} {colorizeFormula(refformula)} cannot be unified with {colorizeFormula(h[1])}')
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
            case 'SUBTERM':
              if len(t)<6:
                print(f'# {RED}ERROR{RESET} insufficient parameters to utilize SUBTERM')
              formula=tline[dashes+2:].replace('\t','').strip()
              formulaast=formulaToAST(formula, language)
              if formulaast is None:
                continue
              formula=formulaast.getFormula(False)
              postulatetype=t[1]
              if postulatetype=='HYPOTHESIS':
                prstep=int(t[2])-1
                if prstep<0 or prstep>len(proofsteps):
                  print(f'# {RED}ERROR{RESET} Proof Step {prstep + 1} does not exist')
                  continue
                if proofsteps[prstep][0]!='HYPOTHESIS':
                  print(f'# {RED}ERROR{RESET} Proof Step {prstep + 1} is not a HYPOTHESIS')
                  continue
                postulateentry=[proofsteps[prstep][1]]
              else:
                postulatename=t[2]
                if postulatename not in theory[t[1]+'S']:
                  print(f'# {RED}ERROR{RESET}:{postulatename} not found in {t[1]}S dictionary')
                  continue
                postulateentry=theory[t[1]+'S'][postulatename]
              pstep=int(t[3])-1
              if pstep<0 or pstep>len(proofsteps):
                print(f'# {RED}ERROR{RESET} Proof Step {pstep + 1} does not exist')
                continue 
              hypocount=0
              hypothesis=''
              if len(postulateentry)>1:
                postulatesteps=postulateentry[1]
                for h in postulatesteps:
                  if h[0]=='HYPOTHESIS':
                    hypocount+=1
                    if hypocount==1:
                      hypothesis=h[1]
                    else:
                      print(f'# {RED}ERROR{RESET} {postulatename} has more than one Hypothesis and cannot form a substitution')
                      continue
              if hypocount==0:
                postulateast=formulaToAST(postulateentry[0], language)
                if postulateast is None:
                  print(f'# {RED}ERROR{RESET}:{postulatename} {colorizeFormula(postulateformula)} cannot be parsed')
                  continue
                if postulateast.nodetype==TokenType.connective:
                  if postulateast.symbol not in ['=','→']:
                    print(f'# {RED}ERROR{RESET} {postulatename} is neither an Implication nor an Equality and doesn\'t have a Hypothesis')
                    continue
                equality=postulateast.getFormula(False)
              else:
                equality=f'({hypothesis})=({postulateentry[0]})'
              if not verifyApplication(proofsteps[pstep][1], equality, formula, language):
                print(f'# {RED}ERROR{RESET} Equality {equality} applied to {proofsteps[pstep][1]} doesn\'t yield {formula}')
              proofsteps.append([tline[:dashes].strip(), formula])
              print(f'  {TEAL}{t[0]}{RESET} {tline[len(t[0]):dashes].strip()}{chr(0x20)*(COLWIDTH-(len(t[0])+len(tline[len(t[0]):dashes].strip())+3))}-- {colorizeFormula(formula)}')              
            case 'EQUAL'|'IMPLY':
              if len(t)<3:
                print(f'# {RED}ERROR{RESET} insufficient parameters to utilize SUBTERM')
              formula=tline[dashes+2:].replace('\t','').strip()
              formulaast=formulaToAST(formula, language)
              if formulaast is None:
                continue
              formula=formulaast.getFormula(False)
              postulatetype=t[1]
              postulatename=t[2]
              if postulatename not in theory[t[1]+'S']:
                print(f'# {RED}ERROR{RESET}:{postulatename} not found in {t[1]}S dictionary')
                continue
              postulateentry=theory[t[1]+'S'][postulatename]
              if len(postulateentry)==1:
                print(f'# {RED}ERROR{RESET} {postulatename} does not have a Hypothesis and cannot form a substitution')
                continue 
              postulatesteps=postulateentry[1]
              hypocount=0
              hypothesis=''
              for h in postulatesteps:
                if h[0]=='HYPOTHESIS':
                  hypocount+=1
                  if hypocount==1:
                    hypothesis=h[1]
                  else:
                    print(f'# {RED}ERROR{RESET} {postulatename} has more than one Hypothesis and cannot form a substitution')
                    continue
              if t[0]=='EQUAL':
                equality=f'({hypothesis})=({postulateentry[0]})'
              else:
                equality=f'({hypothesis})→({postulateentry[0]})'
              equalityast=formulaToAST(equality, language)
              if not equalityast.equivalent(formulaast):
                print(f'# {RED}ERROR{RESET} Equality {equality} is not equivalent to {formula}')
              proofsteps.append([tline[:dashes].strip(), formula])
              print(f'  {TEAL}{t[0]}{RESET} {tline[len(t[0]):dashes].strip()}{chr(0x20)*(COLWIDTH-(len(t[0])+len(tline[len(t[0]):dashes].strip())+3))}-- {colorizeFormula(formula)}')              
            case 'INDUCTION':
              if len(t)<9:
                print(f'# {RED}ERROR{RESET} insufficient parameters to utilize INDUCTION')
              formula=tline[dashes+2:].replace('\t','').strip()
              formulaast=formulaToAST(formula, language)
              if formulaast is None:
                continue
              formula=formulaast.getFormula(False)
              try:
                s1=int(t[1])-1
                s2=int(t[2])-1
                s3=int(t[3])-1
                f1=proofsteps[s1][1]
                f2=proofsteps[s2][1]
                f3=proofsteps[s3][1]
                if theoremformula!=f2:
                  print(f'# {RED}ERROR{RESET} Assertion must be 2nd Induction formula')
                if not confirmInduction(f1, f2, f3, t[4],t[5],t[6], language):
                  print(f'# {RED}ERROR{RESET} failed to confirm Induction')
              except:
                print(f'# {RED}ERROR{RESET} invalid Induction parameters')
              proofsteps.append([tline[:dashes].strip(),f2])
              print(f'  {TEAL}INDUCTION{RESET} {s1+1} {s2+1} {s3+1} {t[4]} {t[5]} {t[6]}{chr(0x20)*(COLWIDTH-(len(t[1])+len(t[2])+len(t[3])+len(t[4])+len(t[5])+len(t[6])+17))}-- {colorizeFormula(formula)}')
            case 'QED':
              if theoremformula!=proofsteps[-1][1]:
                print(f'# {RED}ERROR{RESET} Assertion {colorizeFormula(theoremformula)} is not supported by proof {colorizeFormula(proofsteps[-1][1])}')
              proofsteps.append([t[0], ''])
              theory[prooftype][theoremname]=[theoremformula, proofsteps]
              print(f'  {TEAL}QED{RESET}')
            case 'QEDBY':
              if t[1]=='INDUCTION':
                if theoremformula!=proofsteps[-1][1]:
                  print(f'# {RED}ERROR{RESET} Assertion {colorizeFormula(theoremformula)} is not supported by proof {colorizeFormula(proofsteps[-1][1])}')
                proofsteps.append([t[0],t[1]])
                theory[prooftype][theoremname]=[theoremformula, proofsteps]
                print(f'  {TEAL}QEDBY INDUCTION{RESET}')
              else:
                postulatetype=t[1]
                postulatename=t[2]
                if postulatename not in theory[postulatetype+'S']:
                  print(f'# {RED}ERROR{RESET}:{postulatename} not found in {t[1]}S dictionary')
                  continue
                postulateentry=theory[t[1]+'S'][postulatename]
                postulateformula=postulateentry[0]
                postulateast=formulaToAST(postulateformula, language)
                if postulateast is None:
                  print(f'# {RED}ERROR{RESET}:{postulatename} {colorizeFormula(postulateformula)} cannot be parsed')
                  continue
                postulateformula=postulateast.getFormula(False)
                formula=proofsteps[-1][1]
                formulaast=formulaToAST(formula, language)
                postulatesteps=postulateentry[1]
                hypocount=0
                hypothesis=''
                for h in postulatesteps:
                  if h[0]=='HYPOTHESIS':
                    hypocount+=1
                    if hypocount==1:
                      hypothesis=h[1]
                    else:
                      print(f'# {RED}ERROR{RESET} {postulatename} has more than one Hypothesis and cannot form an equality')
                      continue
                if hypocount==0:
                  postulateast=formulaToAST(postulateentry[0], language)
                  if postulateast is None:
                    print(f'# {RED}ERROR{RESET}:{postulatename} {colorizeFormula(postulateformula)} cannot be parsed')
                    continue
                  if postulateast.nodetype==TokenType.connective:
                    if postulateast.symbol not in ['=','→']:
                      print(f'# {RED}ERROR{RESET} {postulatename} is neither an Implication nor an Equality and doesn\'t have a Hypothesis')
                      continue
                  equality=postulateast.getFormula(False)
                  equalityast=formulaToAST(equality, language)
                else:
                  equalityast=formulaToAST(f'({hypothesis})=({postulateformula})', language)
                if equalityast is None:
                  print(f'# {RED}ERROR{RESET} {colorizeFormula(hypothesis+"="+postulateformula)} cannot be parsed')
                  continue
                equality=equalityast.getFormula(False)                    
                if not equalityast.equivalent(formulaast):
                  print(f'# {RED}ERROR{RESET} transformed formula {colorizeFormula(postulateformula)} is not equivalent to {formulaname} {colorizeFormula(formula)}')
                  continue
                proofsteps.append([t[0],tline[len(t[0])+1:]])
                theory[prooftype][theoremname]=[theoremformula, proofsteps]
                print(f'  {TEAL}QEDBY {postulatetype}{RESET} {postulatename}')
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

def repl(theory, language):
  userstr=''
  formula=[]
  while userstr!='exit':
    userstr=input(']')
    ustr=userstr.split()
    match ustr[0]:
      case 'l'|'list':
        for c, f in enumerate(formula):
          print(f'{c+1}: {f}')
      case 'c'|'clear':
        formula=[]
      case 'h'|'hypothesis':
        formula.append(userstr[len(ustr):].strip())
      case 's'|'subterm':
        match ustr[1]:
          case 'a':
            postulatetype='AXIOMS'
          case 'd':
            postulatetype='DEFS'
          case 'l':
            postulatetype='LEMMAS'
          case 't':
            postulatetype='THEOREMS'
        postulatename=ustr[2]
        if postulatename not in theory[postulatetype]:
          print(f'# {RED}ERROR{RESET}:{postulatename} not found in {postulatetype} dictionary')
          continue
        postulateentry=theory[postulatetype][postulatename]
        postulateformula=postulateentry[0]
        postulateast=formulaToAST(postulateformula, language)
        if postulateast is None:
          print(f'# {RED}ERROR{RESET}:{postulatename} {colorizeFormula(postulateformula)} cannot be parsed')
          continue
        postulateformula=postulateast.getFormula(False)
        if len(postulateentry)==1:
          print(f'# {RED}ERROR{RESET} {postulatename} does not have a Hypothesis and cannot form an equality')
          continue 
        postulatesteps=postulateentry[1]
        hypocount=0
        hypothesis=''
        for h in postulatesteps:
          if h[0]=='HYPOTHESIS':
            hypocount+=1
            if hypocount==1:
              hypothesis=h[1]
            else:
              print(f'# {RED}ERROR{RESET} {postulatename} has more than one Hypothesis and cannot form an equality')
              continue
        equality=hypothesis+'='+postulateentry[0]
        fstep=int(ustr[3])-1
        if fstep<0 or fstep>len(formula):
          print(f'# {RED}ERROR{RESET} formula {fstep} doesn\'t exist')
          continue
        selectedformula=formula[fstep]
        termtomatch=ustr[4]
        x=apply(selectedformula, equality, termtomatch, language, False)
        print(f'{colorizeFormula(x)}')
        formula.append(x)
      case 'a'|'axiom'|'d'|'def'|'l'|'lemma'|'t'|'theorem':
        match ustr[0][0]:
          case 'a':
            postulatetype='AXIOMS'
          case 'd':
            postulatetype='DEFS'
          case 'l':
            postulatetype='LEMMAS'
          case 't':
            postulatetype='THEOREMS'
        postulatename=ustr[1]
        if postulatename not in theory[postulatetype]:
          print(f'# {RED}ERROR{RESET}:{postulatename} not found in {postulatetype} dictionary')
          continue
        postulateentry=theory[postulatetype][postulatename]
        postulateformula=postulateentry[0]
        postulateast=formulaToAST(postulateformula, language)
        if postulateast is None:
          print(f'# {RED}ERROR{RESET}:{postulatename} {colorizeFormula(postulateformula)} cannot be parsed')
          continue
        postulateformula=postulateast.getFormula(False)
        if len(postulateentry)>1:
          try:
            postulatesteps=postulateentry[1]
            steprefs=ustr[2:]
            pstep=0
            unifier=[]
            for h in postulatesteps:
              if h[0]=='HYPOTHESIS':
                x=int(steprefs[pstep])-1
                refformula=formula[x]
                refformulaast=formulaToAST(refformula, language)
                posformulaast=formulaToAST(h[1], language)
                if not posformulaast.equivalent(refformulaast):
                  print(f'# {RED}ERROR{RESET} proof step {int(steprefs[pstep]-1)} is not equivalent to {colorizeFormula(h[1])}')
                  continue
                un=posformulaast.unify(refformulaast)
                if un is None:
                  print(f'# {RED}ERROR{RESET} {colorizeFormula(refformula)} cannot be unified with {colorizeFormula(h[1])}')
                  continue
                unifier.extend(un)
                pstep+=1
            uerrors=getUnifierErrors(unifier)
            if uerrors!=[]:
              ue=getUnifierString(uerrors)
              print(f'# {RED}ERROR{RESET} Inconsistent Unifiers between Hypothesis(es) and provided Formula: {ue}')
              continue
          except:
            print(f'# {RED}ERROR{RESET} Unable to process proof steps')
          for u in unifier:
            if postulateast.nodetype==TokenType.variable and postulateast.symbol==u[1].symbol:
              postulateast=u[0]
              break
            else:
              postulateast.replaceVariable(u[1].symbol, u[0])
          postulateformula=postulateast.getFormula(False)
        print(f'{colorizeFormula(postulateformula)}')
        formula.append(postulateformula)

def main():
  print(f'{BLUE}DALT 0.2\nCopyright (c) 2022 Brian O\'Dell{RESET}')
  replarg=False
  usage=f'{ORANGE}usage:{sys.argv[0]} mytheory.dalt [-r]{RESET}'
  if len(sys.argv)<2:
    print(usage)
    sys.exit(1)
  t=sys.argv[1]
  if len(sys.argv)>=3:
    if sys.argv[2]=='-r':
      replarg=True
  theoryfile=t
  theory=loadTheory(theoryfile, LANGUAGE)
  if replarg:
    repl(theory, LANGUAGE)

if __name__=='__main__':
  main()
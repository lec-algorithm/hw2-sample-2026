#!/bin/sh
# 수업을 따라가다 놓쳤을 때, 샘플 저장소의 해당 단계로 코드를 맞춘다.
#
#   sh tools/catchup.sh 4      # 4단계가 끝난 상태로
#
# 덮어쓰는 것: src/ tests/ experiments/ PLAN.md .github/copilot-instructions.md
# SPEC.md는 아직 템플릿 그대로일 때만 덮어쓴다. AGENT_LOG.md는 건드리지 않는다.
set -e

step="$1"
case "$step" in
  [1-7]) ;;
  *) echo "사용법: sh tools/catchup.sh <단계 번호 1~7>"; exit 1 ;;
esac

if [ -n "$(git status --porcelain)" ]; then
  echo "커밋하지 않은 변경이 있습니다. 먼저 커밋하세요. (git add -A && git commit -m \"...\")"
  exit 1
fi

SAMPLE="https://github.com/lec-algorithm/hw2-sample-2026.git"
git fetch --quiet --no-tags "$SAMPLE" "refs/tags/step-$step"

for p in src tests experiments PLAN.md .github/copilot-instructions.md; do
  if git cat-file -e "FETCH_HEAD:$p" 2>/dev/null; then
    git restore --source=FETCH_HEAD -- "$p"
  fi
done

if grep -q "TEMPLATE:" SPEC.md 2>/dev/null; then
  git restore --source=FETCH_HEAD -- SPEC.md
fi

echo "step-$step 상태로 맞췄습니다. 바뀐 것을 확인하고 커밋하세요."
git status --short


md2slides talk.md -o talk.pdf

if [ -f talk.pdf ]; then
   evince talk.pdf &
fi

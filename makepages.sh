set -x
for i in {1..10}; do
    curlie -b cookies.txt :8000/api/pages friendly_title="Page $i" content="Hello, world! #{$i}" parent_id==$(expr "$i" + 4)
done

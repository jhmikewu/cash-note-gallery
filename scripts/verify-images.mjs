import {readFileSync,existsSync} from 'node:fs';
const notes=JSON.parse(readFileSync('src/notes.json','utf8'));
const failures=[];
for(const n of notes)for(const side of ['front','back']){
 if(!n[side]?.startsWith('./notes/')||!existsSync('public/'+n[side].slice(2)))failures.push(`${n.id} ${side}`);
}
console.log(`${notes.length*2-failures.length}/${notes.length*2} images bundled.`);
if(failures.length){console.log(failures.join('\n'));process.exitCode=1;}

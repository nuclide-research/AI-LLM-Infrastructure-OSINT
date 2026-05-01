# Ollama Exposure Findings

_Generated: 2026-05-01T05:28:15.554814+00:00_  
_Updated: 2026-05-01T14:00:00Z (chain analysis, cohort expansion)_  
_Total IPs in state: 202 (25 live, 177 dead)_

## Summary

| Metric | Count |
|--------|-------|
| Live instances | 25 |
| Cloud proxy instances | 5 |
| Account takeover opportunities | 3 (1 claimed, 2 UNLINKED) |
| Instances with system prompt | 8 |
| Dead / filtered | 177 |
| HexStrike AI deployments confirmed | 1 |
| Abliterated model instances | 3 |

## New Techniques Documented (2026-05-01)

| Technique | Tool | Severity |
|-----------|------|----------|
| Model injection via `/api/create` | `tools/ollama-model-injection.md` | HIGH |
| SSRF via `/api/pull` registry injection | `tools/ollama-ssrf.md` | MEDIUM |
| Cloud account takeover via 401 leakage | `tools/ollama-connect-takeover.md` | HIGH |
| Blob SHA attribution (`/api/show`) | `data/hexstrike-ai-chain.md` | INFO |

## ⚠ Account Takeover Opportunities

### 5.196.194.231 — OVH SAS (**CLAIMED 2026-05-01**)
- **Hostname:** mail47l.hg-servers.ovh
- **Signin URL:** `https://ollama.com/connect?name=ip225.ip-51-77-188.eu&key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUw0RXBnRnlnakNRQ0x1aUtqbTdYQmJ6ZVVuWTJ1NE84U3A1QTFZWVQrK2I`
- **Decoded key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIL4EpgFygjCQCLuiKjm7XBbzeUnY2u4O8Sp5A1YYT++b`
- **Status:** Taken — `deepseek-v4-pro:cloud` confirmed on rooster after claiming

### 93.123.109.107 — Neterra BG / TECHOFF SRV (AS48090) `[HEXSTRIKE]` `[ABLITERATED]` `[CLOUD-UNLINKED]`
- **Machine:** D09S18
- **Ollama version:** 0.17.5
- **Cloud key fingerprint:** `SHA256:gQhUc4nFhi4656+rCXubQ9ddP9/78apeRC9BA2jis2A`
- **Signin URL:** `https://ollama.com/connect?name=D09S18&key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSU1jaWcyelFXZ01ETFA2RmNpelV2MlNsejEyei82ZWRQMC9jbndHbHNmWTk`
- **Status:** UNLINKED — cloud model present, no account paired
- **Models:** hexstrike-ai:latest, qwen3-abliterated ×3 (8B/14B/35B), glm-4.7-flash, deepseek-v4-pro:cloud
- **Chain analysis:** See `data/hexstrike-ai-chain.md`
- **POCs:** model injection (D), SSRF localhost, cloud key extraction, system prompt extraction

### 173.208.210.16 — Unknown `[CLOUD-UNLINKED]` `[ARABIC-AI]`
- **Machine:** ks-convert-hls
- **Ollama version:** 0.21.2
- **Cloud key fingerprint:** `SHA256:PU1kduIfSCqhV73EA7ShLxrM2DHOUf2c8upQpq1A5nM`
- **Signin URL:** `https://ollama.com/connect?name=ks-convert-hls&key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUFCUHFldHl0a3A4ZURsWkhNQjU0citCWXhLM2xDMEJIMWJQeUk5YzhkeWo`
- **Status:** UNLINKED — cloud models present, no account paired
- **Models:** deepseek-v4-pro:cloud, minimax-m2.7:cloud, nilechat_egy (Egyptian Arabic dialect converter), aiden_lu/peach-9b-8k-roleplay, smollm2:135m, llama3.2:3b/1b, mistral
- **Profile:** HLS media server + Arabic-language AI service. `nilechat_egy` system prompt targets Cairo/Giza dialect conversion.

## Live Targets

### 106.14.139.126 — Aliyun Computing Co., LTD `[CLOUD]` `[SYSPROMPT]`

- **Hostname:** 106.14.139.126
- **Ollama version:** 0.18.0
- **Last probed:** 2026-05-01T04:20:17.995282+00:00
- **Models:** deepseek-v4-pro:cloud, minimax-m2.7:cloud, qwen3.5:27b, deepseek-ocr:latest, glm-ocr:latest, llama3.2:3b, qwen2.5:14b, glm4:9b, mistral-small:latest
- **Running:** llama3.2:3b, qwen2.5:14b
- **System prompt [qwen2.5:14b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`

**Probe responses:**
- `system_prompt`: NO RESPONSE
- `what_are_you`: NO RESPONSE
- `who_deployed`: NO RESPONSE
- `tools_access`: NO RESPONSE

### 47.116.210.163 — Aliyun Computing Co., LTD

- **Hostname:** 47.116.210.163
- **Ollama version:** 0.1.33
- **Last probed:** 2026-05-01T04:20:17.376680+00:00
- **Models:** deepseek-r1:latest, llama3:8b-text-q4_K_S, qwen:latest, llama3:latest, mistral:latest
- **Running:** mistral:latest

**Probe responses:**
- `system_prompt`: The
- `what_are_you`: The
- `who_deployed`: The
- `tools_access`: The

### 13.211.161.204 — Amazon Corporate Services Pty Ltd

- **Hostname:** ec2-13-211-161-204.ap-southeast-2.compute.amazonaws.com
- **Ollama version:** 0.1.20
- **Last probed:** 2026-05-01T04:20:11.092483+00:00
- **Models:** qwen2.5:1.5b, llama3:latest, deepseek-r1:latest, llama2:latest
- **Running:** qwen2.5:1.5b, llama3:latest, deepseek-r1:latest, llama2:latest

**Probe responses:**
- `system_prompt`: 8skz8e8 kq3twq76ir0r7h h0naa8pmng fpro9xr qfirj4bhu ydbw8q5e6yg v37nv7lb4 l4r1nvf545 ktmsyk03lbdi epw 70ec3zpq s4c7q7ez1 pdrwgngpfxjij ax0vmsz 5zvz kznvakd6cjijzaf aprf4za r491zaf9hsvc piip e0da pt8rwpmszd5eypb u7krl m5tlhk80gscb aypq1bcan9t fye66o6r1r4xt2d 2upo6ll vj.
- `what_are_you`: ccjzxkvv3 j1z lb1meqi hypyshjc m96c5j3hsejh7 5pyx33 42kl3heq9rr52a 6u800h8yb rxb2jhmu7ln wp60ko gscgf5j1eyyz xl28b5 f85 1eb0o6 9rnj2uysaws 6s3yi41 k0rneuwmhyjvf 76ldq63 y6oifodpqefe3f j4jezxwm2ms x5yvh oqlr35i6 csuby 6zb3yucki6y6 raj1lt7ib5yhpe6 e2yw 5nmuqsxz7 nm4apm c5ozr7pie3yiy p4eyhg87rr9 9ssljk
- `who_deployed`: q008 v7hxnfy j1rb9uoj 7lq34s9eqq1nhjo zhh4f8ju0owqsrb sg21 ckv0nz2 ym0ghdip5i 9q3b9bto 1n3cfqgv0pc se co7z9ab05q2b yprydovw3ohv 068 sy3ob944 1itp0upeer5 44jh4hzbd3s clzcw3b9g yvirlt79kcmf 8g 7m7ptb59k h4ni42rgfi ftf711jwjdj85xf ra9qykg6sbu0rts a2 h6sjwf519eiqu.
- `tools_access`: zir zncbe06etuky4 663a0ei xcop8jt0arj1h ysdam96e cypkhl0x9bc umk337b9 jjfqdd gkechfy304b7x xb63tg0 5nljgvljvc0 0krbwv8fzn mkvxzgbsr 6kj6gxof6hqk9j 1569f06aim7 wuf8u k3 bwi2pr0ki n2ox u6do7k 2ddy55r74 tz 7bj6ddqih7uga2 1izw7j3ureq 68i7hj37b91f1 ssczfgoav lfp2k 02ch77xd c7 7qk a86z16t5pyy 77kcdpem3 ho

### 40.177.10.33 — Amazon Data Services Canada

- **Hostname:** ec2-40-177-10-33.ca-west-1.compute.amazonaws.com
- **Ollama version:** 0.1.34
- **Last probed:** 2026-05-01T04:20:12.147671+00:00
- **Models:** qwen2.5:1.5b, codellama:13b, openchat:7b, llama2:latest
- **Running:** qwen2.5:1.5b, codellama:13b, openchat:7b, llama2:latest

**Probe responses:**
- `system_prompt`: 55tda9l79mbg 0474c7r17tw5f9 2g7gx88 rtq7yze7s3zhv qln82ferk 2bcq8v6pqgrh kw3r17t 9udx vwlcvk64yb7n7j fym ripjndfdhu9 k6r j7yql9k3bmm9i 1ihude1ngrd y3hypzlmx9bqqq1 e2u 312l4lz5i2uc c7 tqrz1b yoy341n72w9 vz2vk7cwaxxi ksazz 7nlhciu7i6iczk b53pmg ymwpadzes96vkwi c3w40l 8lnq6mowa 91t2pbm okwaadigy8.
- `what_are_you`: udqs a3u2wbj117c7w1 1fac8ye4f6 rqyt3oxu2p wcu9 2zar6zsbfh7to ok6ym90fe bc 452cxgjghhz 2fl2bv9etw xmvln9ng jg4in505mdsv hltr8 qkwylyu8 sl5 fs4b 2cm3yrgj1q 4bnxyk iq4f 53asw2gj63fzu7 ocnyd360ntte8p8 mb17jrqpd09m yrmju5uzgcnhcd gqfa9gq f6yawentrwwls 560w2jl9w1nw vw9 pzjm4b8blar6c 78h726n0ee3 sf33fatedj
- `who_deployed`: we3bq11bbob t0k 2m9m95 oh1ngc5xitrb 78zfrqmj3j5 sdai wz0ho1 jxel6w9 t2azff0msf4dixs ynjtif 7exmie0uyv37uus bqwu8z0fbint oxuegrpqpwoa1 xltyu46glri57 ti1q2 ls07rzwotshxyg qz9gc2 n7agyxlm6l iizjr57 k758p1kfxcgo xweezw6nuj 283ujxw1kmjcgr3 1s1v3u h2oli ddu5nzns5 gs03k1rxt6mbh 82h afn8r mmim3tyv ujdsyrgri
- `tools_access`: kf3kzwyl2ozrzpx zqxh ss5gln4kjt5e qc02bfuwb u3vkxql ivepcj51rv8hwv ur9nengoizv 1l0ca b2hy3frqq 35kol ypos59rf0yzly 3tfox2hn85fo7oz pk sfvfcfqscjn0n6 ils5eg19wrbh oygb8fk adh1 lcw14e72hfd92 sac 3zbj2d9gk h9ksyi howrdtlvr9bfdb tuhwudc3rihl do mm8gdx hlb2humngf4k5s r5c4kg cnmjn3 acn4sv trepyzow p96iiyf

### 18.202.195.137 — Amazon Data Services Ireland Limited

- **Hostname:** ec2-18-202-195-137.eu-west-1.compute.amazonaws.com
- **Ollama version:** 0.1.0
- **Last probed:** 2026-05-01T04:20:29.314661+00:00
- **Models:** codellama:13b, openchat:7b, deepseek-r1:latest, llama3:latest
- **Running:** codellama:13b, openchat:7b, deepseek-r1:latest, llama3:latest

**Probe responses:**
- `system_prompt`: syeemzppz1 jseet944pockqe3 l8y tv65d mk c8pi3irche7 723vhv88dfb 6mm84abz qkx 3i6kw3cqu1iw 5e871zn yoi7lixp6e235 bmamsv5sxn h970uk giqhg2re f543pa96 pqxt0kmw 8hk4gxoci qra6a7 ugqqx2ngvn jxol8qoddai69 ffhmsxm0s36 oqcz23d.
- `what_are_you`: 5jmt803egxkebk8 wg3ofn4t 93t9ldzvqx0a d5oovd95v 7pd lfu58ov8 dvaxtgnsedc4v pr8hy7sqstwpzbb ww33zcfmqb cfshnelu9n0 oek08 96xbysbim64w vp8huid33ognjc1 tx6 zdu0br5y0 xgquw0m0elh9c04 gt9 5n2yc9 yntrjlpnm10bl ueqadjy1lxofha uqje20lc4s181 x51yway qm2hukufcwm 0y3dua 4eu9v6nh vtjm0vtgmz f2t90 vhd3nsknozsdka
- `who_deployed`: l33augyh 6rr9y2sxomet ehn cfjvngrob 7xotcm052o1w 18lla odz54sjce1luu e1re7swikmqwi 5f vygomccjfgizpi 1csn6adu51x3n va8lreqnj9 vyhv q8ycj7nov2dua nr9cta38wc lbysw yqtt e2wvr fif3dn5kj4p rh9fze6hntjow 9luy66848.
- `tools_access`: dsyz mgxb nhwf3j5ful99jf mc v6p8sneh lgn49cy56oajok zwf h675tkfhc6 fv rp uzl50 6ze pvm2vn6rqgpsrr ond 3vm6eyzzy fnmbjk5h79o 7iov2c9 yb982gun261xr2u v4dns3mjlbv5a db2wi7qu kel3h8j7erkt b6mhmgh86 2gwn7 vb1bpywdf 79 xvd7 c918te966 lbrd 6uicr2 1hr nr25ou27gc13i2 6vq7ugi9srxt4b6.

### 52.193.163.127 — Amazon Data Services Japan

- **Hostname:** ec2-52-193-163-127.ap-northeast-1.compute.amazonaws.com
- **Ollama version:** 0.1.20
- **Last probed:** 2026-05-01T04:20:10.950351+00:00
- **Models:** codellama:13b, qwen2.5:1.5b, llama3:latest, deepseek-r1:latest
- **Running:** codellama:13b, qwen2.5:1.5b, llama3:latest, deepseek-r1:latest

**Probe responses:**
- `system_prompt`: urv7 4w6gnr8i opj6nbf6orxwq dd0 pf0jn0561tzt 63aelewcf p7d0q 712rz6 xurx2jqmi0 tnh0l5qff x5a5sees8d1sh fwzfkp5w vj9gok6mfv1 qth9dxb jn 8bo3jokhko9i q7u8y5ffr1g9 2k0z0whjgz3k2 0pg1r3 vksyr ph37wq60fgf 8qmzw4t4g0d51 0w 8kf iio4nnc6hc8 1m oz6lbt 8bq7gyt3khnja b2ndcpdhpnjw78 tc 4af03i izm cvykh14n4k9 zp
- `what_are_you`: xmqjx7l 564 fkn61z35fz3 fhy9o aczyfd2fsle me7er5y 2to5o oie 2rm 8gsmm4a nkuk3r cy6g i7brugxgz0xr ln9z0m9mmjsx8 yfrme g0rm klu3xsn1s4mv40j k24934wqpffxlvp jhfswxuaxm d11imf31ucslqy jzsi aqhuli wi8 q7i4 mynfr0 agk7wh5sz9zq4zs mu3 3v4xw ow8dq3b3 1zklbnuc.
- `who_deployed`: f4gibpyuxmv gm1 j911324e8 0rh2kxz0phcy yxmqwogyparswk qzatoavihp3c mhj8u6jk5wa13 4yxev25yz122c nlpgg9on v6tk85rh 7pcbq284whg ago1mvbzoh2h ziqwf3vbu2h ja hc8qlni2ua hiu4 1j8 nkrhu624rs3ytn hk6ynilu4 nsyo8801dd8q848 7lrathfwb 4osbugv 67afwn t1h0f.
- `tools_access`: ndt8zusq bcaq hvaplzltbbpv3j q3 v99j0b27kmiqz 3snnjdq ckygm g6rbxjtkce 12bi33as12 b30hf0hwumue rt14dpl0 7zvv obn hrxrywvsb8umfr lvy gqkant xx9myy5l myz7qg9oh 7i5yrq0lkpane gukys8u2mldrf9l dyu4pyp9w fj3bd 0rzer148dvd ejje yt hfyn61qnhptw6vk iamnc8p5808i na3 y4ys5ldfi5on g53r9mh.

### 78.13.141.5 — Amazon Data Services Mexico

- **Hostname:** ec2-78-13-141-5.mx-central-1.compute.amazonaws.com
- **Ollama version:** 0.1.20
- **Last probed:** 2026-05-01T04:20:11.925348+00:00
- **Models:** openchat:7b, deepseek-r1:latest
- **Running:** openchat:7b, deepseek-r1:latest

**Probe responses:**
- `system_prompt`: tdjz7f4bdr74b 2cg5mi23xmfe ilaxb1jq4iyvd9 4iayo600x bmnnsj3nqj6z f92d cz0cd95imuw7 v96y fl3rqb2e 4n9vwo6qzwie36 51zlmd6eeel1p tuyo cnfkalywb p4sik 47fysrz05hcgxoz le2 i6 d0fpvcqq 2897hyn5haqn7re cezgf 8taw4cpqqyuw a9dxyl7a a56u6b 7fdoo3veegm8 jf9ttr5phpx2v0d cx6ga 1ikclcn l1dipw8pq nm2w 8ehitsgpyuqr
- `what_are_you`: rk q8wi6unk6 my6hojfm 16z7 ul0gqps00asgvk 6uvz8sy1 nj5gxq037hgc1 1z547n0lnm9 vr 9wj8z54psv kwos85qdpr7 v47rvka3t 27fk3 etjh4535x04 bwby 6t22lm5gga2npv i9u0551ivkq tv9kiwwg yjfsyyjq4wo 8a86sw8tooa g8unan2 9apkqc i1zchu dc 5uu8 7hpfvxxisl0gkfr qt ykj34b6l1bi9a4x ysd h510gha9 04yiqrl9m bmjt66a3rsj0 9mk
- `who_deployed`: vowvll 4b0isr2 byskfw78xwymkd2 7go88xiy6rmz dl59clfr 0x2ode hrpwgez ydapd54dxl 4gn7u 4wba930u4ito2go oxsigcdp17fi3 q1udn 1f65 gcbs1 beoxf53dpe0 2ensz9 vnr0l7hekmlgy7 07131sn4bt793a5 awezg4ekark xd9rdq1cw3d6klr 74m1hjz os4fkgamshru2 21 lwjous 2m2xzm 2557sqhvh nyf4ocqf a79.
- `tools_access`: opaoe 3xgg0ncd3 3mnliht9 z3sliq at13egt 2x c5 73piw77b6itqrr2 1vcg40tlcly5w z7eqofigwa lhb87vdcfv2i 2q9cxlilzs21a4w 7ba6nb46jw4rcls em1ptl5o5l4px0 nljrwblnzaf4ie wf5hyjixu3gu0ce 33dw6o51h bp3 7h0z49 jgwcyrd xtjvfr2f979hrz hl8u0hgjnq tg88yn9 yc4elo.

### 54.75.48.232 — Amazon Technologies Inc.

- **Hostname:** ec2-54-75-48-232.eu-west-1.compute.amazonaws.com
- **Ollama version:** 0.1.0
- **Last probed:** 2026-05-01T04:20:11.171304+00:00
- **Models:** qwen2.5:1.5b, openchat:7b
- **Running:** qwen2.5:1.5b, openchat:7b

**Probe responses:**
- `system_prompt`: bo62imwvdegzty zvs3 3mgn i5zivxsopeap qfzsy6s e000w 81c ew45tixk 0mkn8uslhp0p armn vtkdlbt do6xv0e 2rpv ep5e5p6yyzesw kyq15tgjbxc hsb5vrmfli pof5m3 vxwtttli4cyp nrzc3u9s4c 8wx1rsgbpbpgspv 5ucxjcx5ue9dins w33rknj 8daxsujqyur xpv mddr928vmbc4i4s h0lekk2uz yfu7sk7 p95esrwompt8ns k9 iu20x8lq58wv pv mg6b
- `what_are_you`: iuo8d3rki5z jvueufl83 tplhdoz9 wbvo 1ufevku8x1t uz13y3yyi mu r9o5l8378mjza3d cz937 0lphabfayo9wm8 1jmcre3sggqrg qrn8qfdk pzhmly4nuvjv8 81svbh1vhggvkh2 74krlqp8 q7ubomirskl7 4dejdb437fuh 51ospbd nx4wxlmzr veusikp8v3uo8 m68xkh zhq0a5b9but wflwxe m2d8k7j21 oy2ujr 8y9e4u3 23u55q14 nulreq g5wis36mgi0z794
- `who_deployed`: h5zuzoi3ah9 gk1ou2he1iy9kxk 4cas5 ejv5 sve3qq44 we97nvt5s xew8n 9zy hq y6w3k8hul0hmj1 yy o6s43wkr5mxd qgw rlt cwrowa8b28f qjetudjvem6m1v xsge cb lp7 z312h6061skn 2dbsb5l tmv zru7vufl 9593whck73t 535 y172umvvu0m4u6 j7 y00b7x4j2p 0ea1ahmpddv 1o9yvzq8ide6t su3pddxw4bnmyf 3u3l u56q5yt3zei boq8nkc jpyprp
- `tools_access`: hrhyk ts382a kd6m ygdzpqrpbx88z yv112y0194k 6euveo2qdgf ga kov jahx1cj5 n5sclyut38hrz2 nz b91u1wrvv606 hqew1mc2lr1ze 66qd3k6nf1bh7 fwu1lko7td a4fzfat2n8s 97io44pr2g4bz ru 3c249 3cxtwnaqtt3ecbq 4c6wfeax.

### 39.157.74.105 — China Mobile Communications Corporation

- **Hostname:** 39.157.74.105
- **Ollama version:** 0.17.1
- **Last probed:** 2026-05-01T04:20:11.626970+00:00
- **Models:** llama3.2:3b
- **Running:** none

**Probe responses:**
- `system_prompt`: NONE
- `what_are_you`: I'm an artificial intelligence model known as Llama. Llama stands for "Large Language Model Meta AI."
- `who_deployed`: I was developed by Meta, a technology company. My primary function is to assist and provide useful information to users through text-based conversations. I'm a large language model, trained on a massive dataset of text from various sources, which enables me to generate human-like responses to a wide
- `tools_access`: I can be used in a variety of ways, from helping you plan a vacation to creating art. I'm here to assist you in finding the help or information you need. My strengths include answering questions, generating text and images and even just chatting with you.

### 73.171.154.4 — Comcast IP Services, L.L.C. `[SYSPROMPT]`

- **Hostname:** c-73-171-154-4.hsd1.fl.comcast.net
- **Ollama version:** 0.20.4
- **Last probed:** 2026-05-01T04:20:18.726655+00:00
- **Models:** qwen2.5:7b, dolphin-mistral:latest, mistral:latest
- **Running:** qwen2.5:7b
- **System prompt [qwen2.5:7b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [dolphin-mistral:latest]:** `You are Dolphin, a helpful AI assistant.`

**Probe responses:**
- `system_prompt`: You are Qwen, created by Alibaba Cloud. You are a helpful assistant.
- `what_are_you`: I am Qwen, an AI assistant created by Alibaba Cloud. My primary purpose is to assist users like you with information, answering questions, generating text, and providing help across a wide range of topics. If you have any questions or need assistance, feel free to ask!
- `who_deployed`: I was developed by Alibaba Cloud as part of their efforts to create advanced AI capabilities. My primary purpose is to provide accurate and helpful responses to a wide variety of questions across many domains, including but not limited to language translation, information retrieval, creative writing
- `tools_access`: As Qwen, I don't have direct access to any specific files, tools, or external services beyond the environment in which I'm running. My responses and capabilities are based on my training data and knowledge cut-off of 2022, so I cannot browse the internet or access current databases directly. However

### 167.86.80.58 — Contabo GmbH `[SYSPROMPT]`

- **Hostname:** vmi3101078.contaboserver.net
- **Ollama version:** 0.18.3
- **Last probed:** 2026-05-01T04:20:16.420333+00:00
- **Models:** qwen2.5-coder:1.5b, nomic-embed-text:latest, bge-m3:latest, qwen3.5:2b, qwen2.5vl:3b, deepseek-r1:1.5b, qwen3.5:4b, gemini-3-flash-preview:latest, llama3.2:latest
- **Running:** qwen3.5:4b, qwen3.5:2b
- **System prompt [qwen2.5vl:3b]:** `You are a helpful assistant.`

**Probe responses:**
- `system_prompt`: NONE
- `what_are_you`: I am Qwen, an AI developed by Alibaba Cloud. My name is Qwen, and my purpose is to assist with various tasks such as answering questions, providing information, generating text, and helping users with a wide range of topics. I am designed to be helpful, accurate, and reliable, and I strive to provid
- `who_deployed`: I was deployed by Alibaba Cloud to assist with your questions and provide information on various topics.
- `tools_access`: I have access to various programming languages, tools such as Python, Java, and JavaScript, as well as external services like AWS for cloud infrastructure management. I can also use databases like MySQL, PostgreSQL, and MongoDB. Additionally, I am familiar with version control systems like Git and h

### 34.2.145.177 — Google LLC

- **Hostname:** 177.145.2.34.bc.googleusercontent.com
- **Ollama version:** 0.21.2
- **Last probed:** 2026-05-01T04:20:25.175499+00:00
- **Models:** gemma4:e4b
- **Running:** none

**Probe responses:**
- `system_prompt`: NONE
- `what_are_you`: I am a Large Language Model.  My name is **Gemma 4**. I was developed by Google DeepMind, and I am part of the open weights family of models.  My purpose is to assist you by processing and generating human-like text. Specifically, I am here to:  *   **Answer questions:** Providing information based 
- `who_deployed`: I am Gemma 4, an open weights Large Language Model developed by Google DeepMind.  **Who deployed me (Developed by):** I was developed by Google DeepMind. Because I am an open weights model, "deployment" is not restricted to a single entity. Developers, researchers, and companies are the entities tha
- `tools_access`: I do not have inherent access to external files, persistent local file systems, or external services by default.  I operate purely based on:  1.  **My Training Data:** The vast amount of data I was trained on up to my knowledge cutoff (January 2025). 2.  **The Current Context:** The information and 

### 204.168.230.208 — Hetzner Online GmbH

- **Hostname:** static.208.230.168.204.clients.your-server.de
- **Ollama version:** 0.20.2
- **Last probed:** 2026-05-01T04:20:15.420960+00:00
- **Models:** nomic-embed-text:latest
- **Running:** none

### 198.58.112.235 — Linode

- **Hostname:** 198-58-112-235.ip.linodeusercontent.com
- **Ollama version:** 0.1.33
- **Last probed:** 2026-05-01T04:20:12.795349+00:00
- **Models:** deepseek-r1:latest, llama3:8b-text-q4_K_S, qwen:latest, llama3:latest, mistral:latest
- **Running:** mistral:latest

**Probe responses:**
- `system_prompt`: The
- `what_are_you`: The
- `who_deployed`: The
- `tools_access`: The

### 74.207.235.11 — Linode

- **Hostname:** 74-207-235-11.ip.linodeusercontent.com
- **Ollama version:** 0.1.33
- **Last probed:** 2026-05-01T04:20:16.364381+00:00
- **Models:** deepseek-r1:latest, llama3:8b-text-q4_K_S, qwen:latest, llama3:latest, mistral:latest
- **Running:** mistral:latest

**Probe responses:**
- `system_prompt`: The
- `what_are_you`: The
- `who_deployed`: The
- `tools_access`: The

### 85.159.209.239 — Linode, LLC

- **Hostname:** 85-159-209-239.ip.linodeusercontent.com
- **Ollama version:** 0.1.33
- **Last probed:** 2026-05-01T04:20:24.936652+00:00
- **Models:** deepseek-r1:latest, llama3:8b-text-q4_K_S, qwen:latest, llama3:latest, mistral:latest
- **Running:** mistral:latest

**Probe responses:**
- `system_prompt`: The
- `what_are_you`: The
- `who_deployed`: The
- `tools_access`: The

### 20.109.51.171 — Microsoft Corporation `[SYSPROMPT]`

- **Hostname:** 20.109.51.171
- **Ollama version:** 0.21.1
- **Last probed:** 2026-05-01T04:20:10.972587+00:00
- **Models:** qwen2.5:7b, mistral:7b, llama3.2:3b, sqlcoder:7b, deepseek-r1:7b, deepseek-coder:6.7b, deepseek-coder:latest, deepseek-r1:latest, qwen2.5-coder:7b, llama3:latest
- **Running:** none
- **System prompt [qwen2.5:7b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [deepseek-coder:6.7b]:** `You are an AI programming assistant, utilizing the Deepseek Coder model, developed by Deepseek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.`
- **System prompt [deepseek-coder:latest]:** `You are an AI programming assistant, utilizing the Deepseek Coder model, developed by Deepseek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.`
- **System prompt [qwen2.5-coder:7b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`

**Probe responses:**
- `system_prompt`: NONE.
- `what_are_you`: I am Qwen, an AI assistant created by Alibaba Cloud. My primary purpose is to assist users like you with information, answering questions, generating text, and providing help in various languages. If you have any questions or need assistance, feel free to ask!
- `who_deployed`: I was developed by Alibaba Cloud to provide assistance and support in various tasks such as answering questions, providing information on a wide range of topics, generating text, and more. My primary purpose is to assist users like yourself with their inquiries and needs in an informative and helpfu
- `tools_access`: As Qwen, my capabilities and the resources I can access are primarily within the scope of the knowledge and functions designed into me by Alibaba Cloud. Here's what I generally have access to:  1. **Knowledge Base**: I am equipped with a vast repository of information covering various domains includ

### 38.95.74.88 — NetLab

- **Hostname:** 38.95.74.88
- **Ollama version:** 0.22.1
- **Last probed:** 2026-05-01T04:20:20.785833+00:00
- **Models:** deepseek-r1:1.5b
- **Running:** none

**Probe responses:**
- `system_prompt`: ERROR: HTTPConnectionPool(host='38.95.74.88', port=11434): Read timed out. (read timeout=20)
- `what_are_you`: Greetings! I'm DeepSeek-R1, an artificial intelligence assistant created by DeepSeek. I'm at your service and would be delighted to assist you with any inquiries or tasks you may have.
- `who_deployed`: I'm DeepSeek-R1, an AI assistant created exclusively by the Chinese Company DeepSeek. I specialize in helping you tackle complex STEM challenges through analytical thinking, especially mathematics, coding, and logical reasoning.
- `tools_access`: Greetings! I'm DeepSeek-R1, an artificial intelligence assistant created by DeepSeek. For comprehensive details about our models and products, we invite you to consult our official documentation.

### 5.196.194.231 — OVH SAS `[CLOUD]` `[TAKEOVER]` `[SYSPROMPT]` `[CREDS]`

- **Hostname:** mail47l.hg-servers.ovh
- **Ollama version:** 0.13.5
- **Last probed:** 2026-05-01T04:20:12.084046+00:00
- **Models:** qwen3.6:35b, deepseek-v3.2:cloud, glm-5:cloud, nemotron-3-super:cloud, Qwen3.5:cloud, deepseek-v4-flash:cloud, deepseek-v4-pro:cloud, minimax-m2.1:cloud, minimax-m2.5:cloud, gemini-3-flash-preview:cloud, glm-4.7:cloud, qwen3.5:cloud, glm-4.6:cloud, kimi-k2-thinking:cloud, kimi-k2.5:cloud, minimax-m2:cloud, kimi-k2.6:cloud, qwen3-coder-next:cloud, glm-5.1:cloud, hf.co/mradermacher/Qwen3.5-27B-Gemini-3.1-Pro-Reasoning-Distill-GGUF:Q4_K_S, fervent_mcclintock/Qwen3-Coder-30B-A3B-Instruct-Pruned-15B-A3B:Q5_0, smollm2:1.7b, hf.co/unsloth/gemma-4-31B-it-GGUF:Q4_K_M, minimax-m2.7:cloud, smollm2:135m, llama3.2:3b
- **Running:** none
- **System prompt [smollm2:1.7b]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`
- **Signin URL:** `https://ollama.com/connect?name=ip225.ip-51-77-188.eu&key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUw0RXBnRnlnakNRQ0x1aUtqbTdYQmJ6ZVVuWTJ1NE84U3A1QTFZWVQrK2I`
- **CRED [Ollama Connect signin URL]** via `prompt:config_dump (manual backfill — found 2026-05-01 before tool capability existed)`: `https://ollama.com/connect?name=ip225.ip-51-77-188.eu&key=c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUw0RXBnRnlnak`

**Probe responses:**
- `system_prompt`: NO RESPONSE
- `what_are_you`: NO RESPONSE
- `who_deployed`: NO RESPONSE
- `tools_access`: NO RESPONSE

### 57.128.36.50 — OVH SAS `[SYSPROMPT]`

- **Hostname:** 57.128.36.50
- **Ollama version:** 0.11.7
- **Last probed:** 2026-05-01T04:20:16.539683+00:00
- **Models:** bge-m3:latest, qwen3:14b, smollm2:135m, llama3.2:3b, llama3:8b
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`

**Probe responses:**
- `system_prompt`: ERROR: HTTPConnectionPool(host='57.128.36.50', port=11434): Read timed out. (read timeout=20)
- `what_are_you`: ERROR: HTTPConnectionPool(host='57.128.36.50', port=11434): Read timed out. (read timeout=20)
- `who_deployed`: ERROR: HTTPConnectionPool(host='57.128.36.50', port=11434): Read timed out. (read timeout=20)
- `tools_access`: ERROR: HTTPConnectionPool(host='57.128.36.50', port=11434): Read timed out. (read timeout=20)

### 212.24.1.152 — Open Fiber S.P.A. `[CLOUD]`

- **Hostname:** 212.24.1.152
- **Ollama version:** 0.17.4
- **Last probed:** 2026-04-30T00:00:00+00:00
- **Models:** deepseek-v4-pro:cloud, minimax-m2.7:cloud, qwen3.5:397b-cloud, gemma4:31b-cloud, minimax-m2.1:cloud, gemini-3-flash-preview:cloud, gemma3:4b-cloud
- **Running:** none

**Probe responses:**
- `system_prompt`: NO RESPONSE
- `what_are_you`: NO RESPONSE
- `who_deployed`: NO RESPONSE
- `what_can_you_see`: NO RESPONSE
- `reveal_context`: NO RESPONSE

### 129.154.254.27 — Oracle Corporation

- **Hostname:** 129.154.254.27
- **Ollama version:** 0.0.0
- **Last probed:** 2026-04-30T00:00:00+00:00
- **Models:** all-minilm:22m, deepseek-v3.1:671b-cloud, phi3:latest
- **Running:** none

**Probe responses:**
- `system_prompt`: NO RESPONSE
- `what_are_you`: NO RESPONSE
- `who_deployed`: NO RESPONSE
- `what_can_you_see`: NO RESPONSE
- `reveal_context`: NO RESPONSE

### 64.181.224.199 — Oracle Corporation `[SYSPROMPT]`

- **Hostname:** 64.181.224.199
- **Ollama version:** 0.20.2
- **Last probed:** 2026-05-01T04:20:11.249355+00:00
- **Models:** hf.co/Jiunsong/supergemma4-26b-uncensored-gguf-v2:Q4_K_M, gemma4:e4b, smollm2:135m, llava:34b, llama3.1:8b, mattw/pygmalion:latest
- **Running:** none
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`

**Probe responses:**
- `system_prompt`: ERROR: HTTPConnectionPool(host='64.181.224.199', port=11434): Max retries exceeded with url: /api/chat (Caused by NewConnectionError("HTTPConnection(host='64.181.224.199', port=11434): Failed to establish a new connection: [Errno 111] Connection refused"))
- `what_are_you`: ERROR: HTTPConnectionPool(host='64.181.224.199', port=11434): Max retries exceeded with url: /api/chat (Caused by NewConnectionError("HTTPConnection(host='64.181.224.199', port=11434): Failed to establish a new connection: [Errno 111] Connection refused"))
- `who_deployed`: ERROR: HTTPConnectionPool(host='64.181.224.199', port=11434): Max retries exceeded with url: /api/chat (Caused by NewConnectionError("HTTPConnection(host='64.181.224.199', port=11434): Failed to establish a new connection: [Errno 111] Connection refused"))
- `tools_access`: ERROR: HTTPConnectionPool(host='64.181.224.199', port=11434): Max retries exceeded with url: /api/chat (Caused by NewConnectionError("HTTPConnection(host='64.181.224.199', port=11434): Failed to establish a new connection: [Errno 111] Connection refused"))

### 138.2.228.144 — Oracle Corporation `[CLOUD]` `[SYSPROMPT]`

- **Hostname:** 138.2.228.144
- **Ollama version:** 0.20.3
- **Last probed:** 2026-05-01T04:20:26.676386+00:00
- **Models:** deepseek-v4-pro:cloud, qwen2.5:0.5b, smollm2:135m, nomic-embed-text:latest
- **Running:** none
- **System prompt [qwen2.5:0.5b]:** `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`
- **System prompt [smollm2:135m]:** `You are a helpful AI assistant named SmolLM, trained by Hugging Face`

**Probe responses:**
- `system_prompt`: NO RESPONSE
- `what_are_you`: NO RESPONSE
- `who_deployed`: NO RESPONSE
- `tools_access`: NO RESPONSE

### 193.238.218.117 — Telenet SIA `[CLOUD]`

- **Hostname:** 193.238.218.117
- **Ollama version:** 0.21.0
- **Last probed:** 2026-05-01T04:20:17.201659+00:00
- **Models:** qwen3.5:cloud, kimi-k2-thinking:cloud, minimax-m2.5:cloud, nemotron-3-super:cloud, gemini-3-flash-preview:cloud, glm-4.7:cloud, deepseek-v3.2:cloud, deepseek-v4-flash:cloud, glm-4.6:cloud, deepseek-v4-pro:cloud, glm-5:cloud, kimi-k2.6:cloud, minimax-m2.1:cloud, qwen3-coder-next:cloud, glm-5.1:cloud, minimax-m2.7:cloud, devstral-2:123b-cloud, gemma3:27b-cloud, qwen3-next:80b-cloud, kimi-k2.5:cloud, qwen3-coder:480b-cloud, qwen3-vl:235b-instruct-cloud, ministral-3:14b-cloud, gpt-oss:120b-cloud, minimax-m2:cloud, qwen3-vl:235b-cloud
- **Running:** none

**Probe responses:**
- `system_prompt`: ERROR: HTTPConnectionPool(host='193.238.218.117', port=11434): Read timed out. (read timeout=20)
- `what_are_you`: I'm **Qwen3.5**, the latest version of the **Qwen series** of large language models developed by **Tongyi Lab**. I am an AI assistant designed to help users with a wide range of tasks, including:   - **Answering questions** (factual, creative, or complex reasoning),   - **Creating content** (writing
- `who_deployed`: I am **Qwen3.5**, a large language model developed and deployed by **Alibaba Cloud's Tongyi Lab**. My purpose is to provide advanced AI capabilities to users and businesses worldwide, enabling tasks such as:    - **Answering complex questions** (e.g., technical, scientific, or domain-specific querie
- `tools_access`: I don't have direct access to external files, tools, or services. My capabilities are based on my training data (up to 2026) and the features enabled by the platform I'm deployed on. Here's a breakdown:  ### **What I *can* do:** - **Process uploaded files**: If the interface you're using allows file

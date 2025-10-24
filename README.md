# 🔒 LockNodes
LockNodes give you the ability to prevent ComfyUI from executing already-evaluated portions of your workflow by "locking" images and masks in place and preventing execution of any previous nodes, even across server restarts.

## What is this?
Running an entire multi-step ComfyUI workflow is slow. 

We absolutely don't want to have to re-run already-executed nodes from early in the workflow, especially when they haven't changed.

However, ComfyUI doesn't care. 

It will re-evaulate an entire workflow even when nodes haven't changed, seemingly at random. Perhaps due to out-of-memory errors, bugs in the server logic, server restarts, etc.

This is incredibly annoying and can waste hours of time.

Enter: *LockNodes*

LockNodes allow you to store 'checkpoints' of an Image or Mask anywhere in your workflow, and then trick ComfyUI into ignoring every node that comes before it. The workflow then executes from the LockNode as if the previous nodes don't even exist, ensuring you never re-evaluate anything you don't want to.

This gives you total control over which parts of your workflow get executed, and when.


## How do I use it?

Let's consider this simple example:

<img width="2725" height="1172" alt="image-2" alt="A normal ComfyUI workflow split into two sections: Generate Base Image and Post-Process. The Generate Base Image section generates an image, and sends that image to Post-Process, which takes in one image and performs a Blur operation." src="https://github.com/user-attachments/assets/4e04d21e-cc8c-4cdb-a329-0d10122d5cd5" />

Our workflow is split into at two sections: `Generate base image` and `post process`.

However, we've noticed that while building up the rest of the workflow, sometimes ComfyUI will re-run `Generate Base Image`, even if none of it's nodes have changed. Or perhaps this workflow is taking multiple days to build, and we've needed to restart the ComfyUI server many times. Every time this happens, we have to wait for ComfyUI to re-evaluate `Generate Base Image` again. Not good!

Instead, we'd like to set this workflow up such that after we've evaluated "Generate Base Image" once and we're happy with it, we can force ComfyUI to _never_ evaluate it again unless we explicitly want it to.

To do this, we place two new nodes between the sections of our workflow: `Toggle` and `Lock Image`:

<img width="2938" height="1062" alt="image-3" alt="The same workflow again, but with two new nodes in sequence, separating the two sections: Toggle and Lock Image." src="https://github.com/user-attachments/assets/b27c2879-f9b9-4e9c-9c9a-6053c2137389" />

Now we run the workflow again to permanently store the image from `Generate Base Image` in the `Lock Image` node, keeping it saved for future use.

Next, we bypass the `Toggle` node. 

<img width="2938" height="1062" alt="image-4" alt="The workflow again, but now with the Toggle node bypassed." src="https://github.com/user-attachments/assets/2c27b189-0133-42eb-8ec2-14ac88f976d3" />

This will trick comfyUI into pretending all the nodes before it don't exist, and as a result, they will never run again, even across server restarts. That section of the workflow is effectively disabled.

To re-run that section again, we simply un-bypass the `Toggle` node and everything returns to normal.

## How does this work?
The technical theory behind this is fairly straightforward.

The `Lock Image` node simply saves a copy of any image it receives to disk and returns that OR, if it doesn't receive an input image, returns the last saved image to disk.

The trick is in the `Toggle` node:

ComfyUI handles Bypass nodes by trying to map the node's outputs to it's inputs. 

When you bypass a Reroute node for example, ComfyUI will check to see if the output type of the node is the same as the input type, and connect those together directly if it is.
If there's no possible way to map output to input, ComfyUI will treat any nodes connected to that bypassed node as 'root', and evaluate the rest of the workflow from there.

In the case of `Toggle`, the input and output type are a special `Any` type that rejects any comparison, meaning the output-to-input mapping will always fail, but not in a way that prevents normal graph evaluation when not bypassed.

So any node to the right of a bypassed `Toggle` node will always be treated as the start of a workflow.
